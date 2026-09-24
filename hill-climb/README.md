# Desi Hill Drive
A modular static HTML5 hill-climb racing game for GitHub Pages. The existing root game in this repository is preserved; this project lives under /hill-climb/.

## Run
Open the GitHub Pages /hill-climb/ path. For local development use a local HTTP server because ES modules do not run correctly from file://.

## Controls
Mobile: Brake and Gas pedals. Desktop: Arrow keys or WASD. Portrait displays a rotate prompt. Use ?debug=1 for the debug overlay and ?selftest=1 for tuning checks.

## Add a vehicle in 5 steps
1. Open src/vehicles/vehicles.js.
2. Add one data object with a unique id.
3. Define chassis mass/COM, wheels, engine, air torque and fuel.
4. Add optional art under assets/vehicles/<id>/.
5. Refresh Garage. Tractor is the full reference example already included.

## Add a map
Add a data object to src/maps/maps.js with id, seed, roughness, friction and palette. The terrain and renderer consume map data automatically.

## Sprites
Vehicle files: assets/vehicles/<id>/body.png, wheel_front.png, wheel_rear.png, optional fork.png and meta.json. Driver files: assets/drivers/<id>/head.png, head_crash.png, torso.png, arm.png, leg.png and meta.json. Missing assets use procedural rendering.

## Where to tweak feel
src/config.js controls fixed timestep and physics defaults. src/vehicles/vehicles.js controls mass, COM, torque, speed, wheel friction, suspension, fuel and air torque.

## Folder guide
src/main.js boots the game. src/game.js owns the physics/render loop. src/world contains terrain, camera, decor, particles, pickups and lighting. src/vehicles contains vehicle data, physics construction, upgrades, drivers and renderer. src/maps contains map data. ART_PROMPTS.md is the art pack.

## GitHub Pages
This folder is static and requires no build step. The repository's existing Pages workflow can serve it at /hill-climb/.