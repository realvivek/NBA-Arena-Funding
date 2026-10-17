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

// A block of copy: a paragraph, a chart, a subhead, a pull quote, a chart told in steps as the reader scrolls
// (each step names the chart state it shows), or the arena lookup. Paragraphs and steps cite sources by id.
const step = z.object({ step: z.string(), p: z.string(), sources: cites }).strict();
const block = z.union([
  z.object({ p: z.string(), sources: cites }).strict(),
  z.object({ fig: z.string() }).strict(),
  z.object({ h3: z.string() }).strict(),
  z.object({ quote: z.string(), by: z.string(), sources: cites }).strict(),
  z.object({ scrolly: z.string(), steps: z.array(step).min(2) }).strict(),
  z.object({ lookup: z.string(), title: z.string(), intro: z.string(), sources: cites }).strict(),
]);
// A chapter ends with a link to the reference page that holds its full record.
const more = z.object({ page: z.string(), text: z.string() }).strict();

// The story on the home page, one entry per section, in order of n.
const story = defineCollection({
  loader: file('src/content/story.yaml'),
  schema: z.object({
    n: z.number().int(),
    title: z.string().optional(),
    blocks: z.array(block),
    more: z.array(more).default([]),
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
    // the home page's "What we found": one line per finding, each pointing to the chapter that holds it
    findings: z.array(z.object({ p: z.string(), to: z.string(), sources: cites }).strict()).default([]),
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
