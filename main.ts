// main.ts — places this entry's image where the make.fun harness expects it.
//
// The harness runs this file with the working directory set to the
// entry folder and reads the finished picture from $MAKEFUN_OUTPUT_DIR
// (falling back to ./output when the variable is absent). This file only
// copies the pre-rendered entry.png there; all drawing happens in draw.py.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = resolve(here, "entry.png");

if (!existsSync(sourcePath)) {
  throw new Error(`entry.png missing beside main.ts: ${sourcePath}`);
}

const outputDir = process.env.MAKEFUN_OUTPUT_DIR
  ? resolve(process.env.MAKEFUN_OUTPUT_DIR)
  : resolve(here, "output");
mkdirSync(outputDir, { recursive: true });

const destination = join(outputDir, "entry.png");
const image = readFileSync(sourcePath);
writeFileSync(destination, image);

console.log(`copied ${image.length} bytes to ${destination}`);
