# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the official website for **CURE (Center for Unconventional Resources & Energy)** at Inha University, a Jekyll static site hosted on GitHub Pages. The lab focuses on AI-powered subsurface engineering (CO₂ storage, hydrogen storage, digital rock physics).

## Development Commands

```bash
bundle install              # Install Ruby gem dependencies
bundle exec jekyll serve    # Serve locally at http://localhost:4000 with file watching
bundle exec jekyll build    # Build to _site/ for production
```

Requires Ruby and Bundler. The `_site/` directory is git-ignored and auto-generated.

## Architecture

**Framework:** Jekyll 4.3.2 with the minima ~2.5 theme and jekyll-feed plugin. Content is written in Markdown with Liquid templating; Kramdown processes Markdown.

**Page structure:** All major pages are Markdown files at the root level with numeric prefixes indicating nav order:
- `index.markdown` — Homepage with image carousel (vanilla JS) and scroll-reveal animations
- `i_1_members.markdown` — Team profiles page
- `i_3_Lectures.markdown` — Course listings
- `i_4_Publications.markdown` — Publications list organized by year
- `i_5_Projects.markdown` — Funded research projects
- `i_6_.markdown` — IsCUE 2026 Symposium details

**Blog posts** live in `_posts/` as dated Markdown files (English and Korean mix). Archived/deprecated posts are in `_depreciated/`.

**Images** are stored in `_images/` and referenced via relative paths like `/_images/filename.jpg`.

## Styling Conventions

Each page uses **inline `<style>` blocks** — there is no separate CSS file. The site's primary color is `#005BAC` (blue). Common patterns:
- Responsive grids via `grid-template-columns: repeat(auto-fit, minmax(..., 1fr))`
- Card components with `border-radius`, `box-shadow`, hover transitions
- `@media (max-width: 900px)` breakpoint for mobile layouts
- `@media (prefers-reduced-motion: reduce)` for accessibility

JavaScript is vanilla (no frameworks), used only for the homepage image slider and scroll-triggered fade-in animations. These scripts are embedded directly in `index.markdown`.

## Config

`_config.yml` sets site metadata (title, email, description, social links). The `github_username` is `PetroInha`. Navigation links are defined there under `header_pages`.
