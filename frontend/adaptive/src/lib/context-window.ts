import type { HistoryTurn } from '$lib/types/exploration';

const MAX_CONTEXT_TABLE_ROWS = 100;

const WINDOW_TIERS = [
  { maxWords: 2_500, messageCount: 12 },
  { maxWords: 5_000, messageCount: 8 },
  { maxWords: 10_000, messageCount: 4 },
  { maxWords: Number.POSITIVE_INFINITY, messageCount: 2 }
] as const;

function isResultTurn(
  turn: HistoryTurn
): turn is HistoryTurn & {
  columns: NonNullable<HistoryTurn['columns']>;
  rows: NonNullable<HistoryTurn['rows']>;
} {
  return turn.role === 'assistant' && Array.isArray(turn.columns) && Array.isArray(turn.rows);
}

function countWords(value: unknown): number {
  if (typeof value === 'string') {
    return value.trim().match(/\S+/gu)?.length ?? 0;
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return 1;
  }

  if (Array.isArray(value)) {
    return value.reduce((total, item) => total + countWords(item), 0);
  }

  if (value && typeof value === 'object') {
    return Object.entries(value).reduce(
      (total, [key, item]) => total + countWords(key) + countWords(item),
      0
    );
  }

  return 0;
}

function compactHistory(history: HistoryTurn[]): HistoryTurn[] {
  const newestResultIndex = history.findLastIndex(isResultTurn);

  return history.map((turn, index) => {
    if (turn.role === 'user') {
      return { role: 'user', content: turn.content };
    }

    const compactTurn: HistoryTurn = {
      role: 'assistant',
      content: turn.content,
      observations: turn.observations,
      sparql_query: turn.sparql_query,
      ...(turn.interpretation && turn.interpretation !== turn.content
        ? { interpretation: turn.interpretation }
        : {})
    };

    if (index === newestResultIndex && isResultTurn(turn)) {
      compactTurn.columns = turn.columns;
      compactTurn.rows = turn.rows;
    }

    return compactTurn;
  });
}

function limitNewestResultRows(turn: HistoryTurn): HistoryTurn {
  if (!isResultTurn(turn) || turn.rows.length <= MAX_CONTEXT_TABLE_ROWS) return turn;

  const originalRowCount = turn.rows.length;
  const contextNote =
    `[Context note: Only the first ${MAX_CONTEXT_TABLE_ROWS} of ${originalRowCount} result rows are included here; the remaining rows are omitted from the request history.]`;

  return {
    ...turn,
    content: turn.content ? `${turn.content}\n\n${contextNote}` : contextNote,
    rows: turn.rows.slice(0, MAX_CONTEXT_TABLE_ROWS)
  };
}

/**
 * Returns a compact recent window for the API while leaving the full history
 * and result data untouched in the UI store.
 */
export function buildContextWindow(history: HistoryTurn[], currentMessage: string): HistoryTurn[] {
  const compacted = compactHistory(history);
  const contextWordCount = countWords({ history: compacted, message: currentMessage });
  const tier = WINDOW_TIERS.find(({ maxWords }) => contextWordCount <= maxWords)!;
  const newestResultIndex = compacted.findLastIndex(isResultTurn);

  if (contextWordCount > 10_000) {
    return newestResultIndex >= 0
      ? [limitNewestResultRows(compacted[newestResultIndex])]
      : [];
  }

  const priorMessageCount = tier.messageCount - 1;
  if (priorMessageCount === 0 || compacted.length === 0) return [];

  const includedCount = Math.min(priorMessageCount, compacted.length);
  const selectedIndexes = new Set(
    Array.from({ length: includedCount }, (_, index) => compacted.length - includedCount + index)
  );

  if (newestResultIndex >= 0 && !selectedIndexes.has(newestResultIndex)) {
    const oldestSelectedIndex = Math.min(...selectedIndexes);
    selectedIndexes.delete(oldestSelectedIndex);
    selectedIndexes.add(newestResultIndex);
  }

  return [...selectedIndexes]
    .sort((a, b) => a - b)
    .map((index) => compacted[index]);
}
