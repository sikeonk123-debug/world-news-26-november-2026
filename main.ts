// The World in One Day — Thursday 26 November 2026.
//
// Entrypoint for the make.fun bounty "Sum up 26 November's world
// news in one image". The front page itself is drawn by draw.py and
// committed as entry.png; this program simply places that finished
// image where the grader expects it, at /output/entry.png.
//
// The destination can be overridden for local testing:
//   OUTPUT_PATH=/tmp/out/entry.png node main.ts

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, "entry.png");
const target = process.env.OUTPUT_PATH ?? "/output/entry.png";

mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);
console.log(`Wrote ${target}`);
