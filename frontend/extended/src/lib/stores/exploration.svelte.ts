import { getMockData, unsupportedResponse } from '$lib/data/mock-data';
import type { Facet, Filter, SortState, LoadingStage, ErrorState, GeneratedPrompt, FacetRow, Observation, FollowUpQuestion } from '$lib/types/exploration';

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function isUnsupported(question: string): boolean {
  const lower = question.toLowerCase();
  const unsupportedPatterns = ['citations', 'h-index', 'impact factor', 'co-author', 'download', 'full text'];
  return unsupportedPatterns.some(p => lower.includes(p));
}

function generatePromptText(
  filterValue: string | number,
  _fromFacet: Facet,
  toFacet: Facet
): string {
  if (toFacet === 'venue') return `Which venues has ${filterValue} published in?`;
  if (toFacet === 'year') return `How has ${filterValue}'s publication output changed over time?`;
  if (toFacet === 'author') return `Who are the most active authors at ${filterValue}?`;
  return `Explore ${filterValue} by ${toFacet}`;
}

function createExplorationStore() {
  let input = $state('');
  let targetFacet = $state<Facet | null>(null);
  let filters = $state<Filter[]>([]);
  let sorting = $state<SortState | null>(null);
  let rows = $state<FacetRow[]>([]);
  let observations = $state<Observation[]>([]);
  let followUpQuestions = $state<FollowUpQuestion[]>([]);
  let loadingStage = $state<LoadingStage>(null);
  let error = $state<ErrorState | null>(null);
  let promptOutputMode = $state<'input' | 'tooltip'>('tooltip');
  let generatedPrompt = $state<GeneratedPrompt | null>(null);
  let hasSubmitted = $state(false);
  let tooltipPosition = $state({ x: 0, y: 0 });

  async function submitQuestion(question: string) {
    if (!question.trim() || loadingStage !== null) return;

    input = question.trim();
    hasSubmitted = true;
    error = null;
    generatedPrompt = null;

    loadingStage = 'interpreting';
    await delay(600);

    loadingStage = 'preparing';
    await delay(400);

    loadingStage = 'querying';
    await delay(800);

    loadingStage = 'analyzing';
    await delay(500);

    if (isUnsupported(question)) {
      loadingStage = null;
      error = {
        type: 'unsupported',
        message: unsupportedResponse.message,
        suggestions: unsupportedResponse.suggestions
      };
      return;
    }

    const data = getMockData('author', []);
    targetFacet = 'author';
    filters = [];
    sorting = null;
    rows = data.rows;
    observations = data.observations;
    followUpQuestions = data.followUps;
    loadingStage = null;
  }

  function pivotCell(rowIndex: number, clickedFacet: Facet) {
    if (rows.length === 0 || targetFacet === null) return;

    const row = rows[rowIndex];
    const currentTarget = targetFacet;

    const newFilter: Filter = {
      field: currentTarget,
      operator: '=',
      value: row.targetValue
    };

    const exists = filters.some(f => f.field === newFilter.field && f.value === newFilter.value);
    const newFilters = exists ? [...filters] : [...filters, newFilter];

    filters = newFilters;
    targetFacet = clickedFacet;

    const data = getMockData(clickedFacet, newFilters);
    rows = data.rows;
    observations = data.observations;
    followUpQuestions = data.followUps;
    sorting = null;

    generatedPrompt = {
      text: generatePromptText(row.targetValue, currentTarget, clickedFacet),
      targetCell: { rowIndex, facet: clickedFacet }
    };

    if (promptOutputMode === 'input') {
      input = generatedPrompt.text;
    }
  }

  function removeFilter(index: number) {
    filters = filters.filter((_, i) => i !== index);

    if (filters.length === 0) {
      targetFacet = null;
      rows = [];
      observations = [];
      followUpQuestions = [];
    } else {
      const data = getMockData(targetFacet!, filters);
      rows = data.rows;
      observations = data.observations;
      followUpQuestions = data.followUps;
    }
    sorting = null;
    generatedPrompt = null;
  }

  function sortFacet(facet: Facet) {
    if (sorting && sorting.facet === facet) {
      if (sorting.direction === 'asc') {
        sorting = { facet, direction: 'desc' };
      } else {
        sorting = null;
      }
    } else {
      sorting = { facet, direction: 'asc' };
    }

    if (sorting) {
      rows = [...rows].sort((a, b) => {
        const aVal = a.connections[facet];
        const bVal = b.connections[facet];
        const numA = typeof aVal === 'number' ? aVal : 0;
        const numB = typeof bVal === 'number' ? bVal : 0;
        return sorting!.direction === 'asc' ? numA - numB : numB - numA;
      });
    }
  }

  function selectFollowUp(question: string) {
    input = question;
    submitQuestion(question);
  }

  function togglePromptMode() {
    promptOutputMode = promptOutputMode === 'input' ? 'tooltip' : 'input';
    generatedPrompt = null;
  }

  function clearPrompt() {
    generatedPrompt = null;
  }

  function setTooltipPosition(x: number, y: number) {
    tooltipPosition = { x, y };
  }

  function reset() {
    input = '';
    targetFacet = null;
    filters = [];
    sorting = null;
    rows = [];
    observations = [];
    followUpQuestions = [];
    loadingStage = null;
    error = null;
    generatedPrompt = null;
    hasSubmitted = false;
  }

  return {
    get input() { return input; },
    set input(v: string) { input = v; },
    get targetFacet() { return targetFacet; },
    get filters() { return filters; },
    get sorting() { return sorting; },
    get rows() { return rows; },
    get observations() { return observations; },
    get followUpQuestions() { return followUpQuestions; },
    get loadingStage() { return loadingStage; },
    get error() { return error; },
    get promptOutputMode() { return promptOutputMode; },
    get generatedPrompt() { return generatedPrompt; },
    get hasSubmitted() { return hasSubmitted; },
    get tooltipPosition() { return tooltipPosition; },
    submitQuestion,
    pivotCell,
    removeFilter,
    sortFacet,
    selectFollowUp,
    togglePromptMode,
    clearPrompt,
    setTooltipPosition,
    reset
  };
}

export const explorationStore = createExplorationStore();
