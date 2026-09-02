# Image prompts

Four images are used. Generate each with your tool of choice, save it at the exact
path below, and it will slot into the README automatically. Architecture and data-flow
diagrams are NOT images: they are Mermaid, rendered by GitHub, so they stay accurate
and editable. Use image generation only for the atmospheric pieces below.

Style rules for every image: photographic or painterly realism, restrained palette,
one focal subject, no text in the image (generators misspell it), no charts, no
candlesticks, no coins, no glowing circuit boards, no robots, no "AI" iconography.
The tone is quiet industrial seriousness, like a control room at 4 a.m.

---

## 1. `assets/hero.jpg` — repo banner and social preview
Size: 1280 × 640 (GitHub social preview ratio 2:1). Also upload this one under
Settings → General → Social preview.

Prompt:
> A heavy steel blast door, slightly ajar, in a dim concrete corridor. Warm light
> leaks through the gap; the corridor is cold blue-grey. A single red indicator lamp
> is lit beside the door. Photorealistic, 35mm lens, shallow depth of field, film
> grain, cinematic contrast. No people, no text, no signage.

Why: the system is a door that is closed by default and opens only when eleven
conditions hold. The image should feel like restraint, not danger.

## 2. `assets/gates.jpg` — section header for "Eleven gates"
Size: 1600 × 600.

Prompt:
> A long row of identical steel lock gates on a canal at dawn, receding into mist,
> each gate closed, water still. Overhead view at a low angle, muted greens and
> greys, soft fog, one gate in the far distance catching sunlight. Photorealistic,
> no text, no people, no boats.

Why: independent barriers in series, all closed by default.

## 3. `assets/log.jpg` — section header for "The log is the database"
Size: 1600 × 600.

Prompt:
> A close-up of a paper seismograph drum, the needle mid-trace, ink line continuous
> and unbroken across the page, dramatic side lighting on the paper texture. Warm
> monochrome, macro lens, very shallow focus. No text visible on the paper.

Why: an append-only record that is written once and read many ways.

## 4. `assets/refuse.jpg` — closing image
Size: 1600 × 600.

Prompt:
> An empty trading floor at night seen from the mezzanine, every screen dark except
> one, which shows only a flat horizontal line. Cool ambient light, long exposure,
> reflections on polished floor, no people. Photorealistic, quiet, slightly eerie.

Why: a system that has been ready for months and has chosen, every day, not to act.

---

## 5. Optional: `dashboard.mp4` — a 60 to 90 second screen recording (not an image)

Hiring managers want to see working software. Record the operator dashboard during a
paper-mode session on a market day: set the line, watch a candle close, watch an entry
get built and refused by a gate, hit the kill switch. No narration needed; no real
account identifiers on screen (paper mode shows none). Keep it under 10 MB (H.264).

Upload rule from GitHub: drag the .mp4 into the README web editor ONLY AFTER the repo is
public. Attachments uploaded while a repo is private get private URLs that break when
the repo goes public. Leave the resulting github.com/user-attachments/assets URL on its
own line in the README where the `<!-- dashboard video -->` marker is.
