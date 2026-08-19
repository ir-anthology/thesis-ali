import type { Entity } from '$lib/types/exploration';

export const mockAuthors: Entity[] = [
  {
    id: 'a1',
    name: 'Marti A. Hearst',
    type: 'author',
    facets: { publications: 42, venues: 12, years: '1995–2024' }
  },
  {
    id: 'a2',
    name: 'Ryen W. White',
    type: 'author',
    facets: { publications: 38, venues: 10, years: '2003–2024' }
  },
  {
    id: 'a3',
    name: 'Gary Marchionini',
    type: 'author',
    facets: { publications: 31, venues: 9, years: '1997–2023' }
  },
  {
    id: 'a4',
    name: 'Daniel M. Russell',
    type: 'author',
    facets: { publications: 27, venues: 8, years: '2000–2022' }
  },
  {
    id: 'a5',
    name: 'Andrei Z. Broder',
    type: 'author',
    facets: { publications: 24, venues: 7, years: '1998–2021' }
  }
];

export const mockVenues: Entity[] = [
  {
    id: 'v1',
    name: 'SIGIR',
    type: 'venue',
    facets: { publications: 88, years: '1971–2025' }
  },
  {
    id: 'v2',
    name: 'CHIIR',
    type: 'venue',
    facets: { publications: 32, years: '2016–2025' }
  },
  {
    id: 'v3',
    name: 'CHI',
    type: 'venue',
    facets: { publications: 25, years: '1982–2025' }
  },
  {
    id: 'v4',
    name: 'UIST',
    type: 'venue',
    facets: { publications: 18, years: '1988–2025' }
  },
  {
    id: 'v5',
    name: 'JASIST',
    type: 'venue',
    facets: { publications: 15, years: '1950–2025' }
  }
];

export const mockPublications: Entity[] = [
  {
    id: 'p1',
    name: 'User Interfaces and Support for Exploratory Search',
    type: 'publication',
    facets: { author: 'Marti A. Hearst', venue: 'SIGIR', year: 2023 }
  },
  {
    id: 'p2',
    name: 'Search Interaction Patterns in Exploratory Tasks',
    type: 'publication',
    facets: { author: 'Ryen W. White', venue: 'CHIIR', year: 2022 }
  },
  {
    id: 'p3',
    name: 'Faceted Search for Digital Libraries',
    type: 'publication',
    facets: { author: 'Gary Marchionini', venue: 'JASIST', year: 2021 }
  }
];
