/**
 * tcm_aspects.js
 * Placeholder module for TCM aspect utilities.
 */

export const tcmAspects = [
  // Define TCM aspects here.
];

export function findAspect(name) {
  return tcmAspects.find((aspect) => aspect.name === name) || null;
}
