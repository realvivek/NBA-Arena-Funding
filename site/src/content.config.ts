import { defineCollection, reference } from 'astro:content';
import { file } from 'astro/loaders';
import { z } from 'astro/zod';

// The bibliography, written by pipeline/build.py from pipeline/sources.yaml. Copy cites these ids.
const sources = defineCollection({
  loader: file('src/generated/sources.json'),
  schema: z.object({
    url: z.url(),
    title: z.string().min(3),
    title_from: z.enum(['ledger description', 'page title', 'url', 'curated']),
    publisher: z.string(),
    origin: z.enum(['government', 'court', 'team_or_league', 'independent']),
    date: z.string().regex(/^(\d{4}(-\d{2}(-\d{2})?)?|n\.d\.)$/),
    checked: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    review: z.string().optional(),
  }),
});

const cites = z.array(reference('sources')).default([]);

// A block of copy: a paragraph, a chart, a subhead or a pull quote. Paragraphs cite sources by id.
const block = z.union([
  z.object({ p: z.string(), sources: cites }).strict(),
  z.object({ fig: z.string() }).strict(),
  z.object({ h3: z.string() }).strict(),
  z.object({ quote: z.string(), by: z.string(), sources: cites }).strict(),
]);

// The story on the home page, one entry per section, in order of n.
const story = defineCollection({
  loader: file('src/content/story.yaml'),
  schema: z.object({
    n: z.number().int(),
    title: z.string().optional(),
    blocks: z.array(block),
  }),
});

// Heads and copy for the story and the reference pages.
const pages = defineCollection({
  loader: file('src/content/pages.yaml'),
  schema: z.object({
    path: z.string(),
    kicker: z.string(),
    title: z.string(),
    deck: z.string(),
    description: z.string(),
    sources: cites,
    tiles: z.array(z.object({ value: z.string(), label: z.string() })).default([]),
    blocks: z.array(block).default([]),
    notes: z.array(block).default([]),
  }),
});

// Chart frames: the finding as a title, what is plotted, the legend, notes and extra sources.
const figures = defineCollection({
  loader: file('src/content/figures.yaml'),
  schema: z.object({
    title: z.string(),
    sub: z.string(),
    dataset: z.string(),
    // strict: an unquoted comma in a YAML flow mapping would otherwise split a label into a stray key
    legend: z.array(z.object({ label: z.string(), key: z.string() }).strict()).default([]),
    notes: z.array(z.string()).default([]),
    sources: cites,
  }),
});

export const collections = { sources, story, pages, figures };
