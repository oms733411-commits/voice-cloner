/* Load.js - maps are already embedded in maps.js for this Paji Mario build. */
function startLoadingMaps() { return; }
function passivelyLoadMap() { return; }
function setNextLevelArr(arr) {
  if(arr[1]++ == 4) { ++arr[0]; arr[1] = 1; }
  return arr;
}