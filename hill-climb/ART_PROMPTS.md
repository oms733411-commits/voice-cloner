# ART_PROMPTS.md

## A. Style lock
Every prompt must start with:
2D game sprite, strict side profile view facing right, orthographic (no perspective, no 3/4 view), cartoon style like a mobile hill-climb racing game, bold saturated colors, thick smooth dark outlines, soft cel shading, light from top-left, slightly exaggerated proportions, clean vector-like look. Transparent background, single object centered, nothing cropped, no ground, no shadow, no text, no logos, no brand names, no watermark.

## B. Vehicle prompts
1. commuter-bike: simple Indian 100cc commuter motorcycle, slim, black and red, chrome exhaust.
2. bullet-cruiser: classic Indian 350cc cruiser, teardrop dark green tank, chrome, round headlight, long silencer.
3. sport-bike: sporty Indian 220cc street bike, aggressive fairing, black and blue tank, upswept exhaust.
4. auto-rickshaw: yellow and green three-wheeler, black canopy roof, open sides, rounded cute shape, side view with one front and one rear wheel.
5. small-hatchback: small old-school boxy Indian hatchback, white or light blue, round headlight.
6. tractor: red-orange farm tractor, tall exhaust pipe, open seat with small canopy, big rear fender.
7. offroad-4x4: boxy soft-top off-road 4x4, rugged bumper, round headlights, rear spare wheel, roll bar, orange or dark red.
8. suv-big: big tall SUV, muscular grille, roof rails, black or silver, large windows.

For each vehicle prepend the exact Style Lock paragraph. Generate body only with no wheels; use generic designs and no real logos or brand names.

## C. Wheel prompt
Single wheel in perfect side view, perfect circle filling the square canvas, transparent background. Variants: thin spoked alloy for bikes, alloy rim with thick tread for cars, deep-lug agricultural tire for tractor, small steel rim with chunky tire for auto.

## D. Driver prompts
Generate the full seated character first, then cut into head.png, head_crash.png, torso.png, arm.png and leg.png.
- kisan-kaka: friendly farmer, colorful pagdi, mustache, white kurta with vest.
- rani: young girl, bright helmet, flowing dupatta, denim jacket.
- jawan: army-style rider, olive cap, no real insignia.
- chotu: school kid, oversized helmet, school bag.
Use the Style Lock above for each character prompt.

## E. Getting separate parts
Method A: generate the full vehicle, cut wheels out in Photopea/Photoshop and paint the empty wheel wells. Method B: generate body-only with empty wheel wells and a separate single wheel with the same style lock. Generate at 2048 px, remove the background and downscale.

## F. Target sizes
| Vehicle | body.png | wheel |
| commuter-bike | 400x230 | 124 |
| bullet-cruiser | 420x240 | 132 |
| sport-bike | 410x240 | 124 |
| auto-rickshaw | 540x380 | 100 |
| small-hatchback | 680x300 | 120 |
| tractor | 700x420 | rear 260, front 160 |
| offroad-4x4 | 780x380 | 170 |
| suv-big | 900x400 | 160 |
Drivers: head about 90 px, torso about 110x160, arm about 100 long, leg about 130 long. Wheels are perfect squares with the circle touching all four edges. PNG 32-bit transparent.

## G. Optional map layers
Generate 2048x1024 horizontally seamless transparent-sky layers. Village: far misty hills, mid fields + mud houses + small temple, near banyan/coconut trees, golden hour. Ladakh: far snow peaks in blue haze, mid rocky slopes + monastery, near pines + prayer flags. Save as assets/maps/<mapId>/far.png, mid.png and near.png.

## H. Sprite pipeline and meta.json
Vehicle: assets/vehicles/<id>/body.png, wheel_front.png, wheel_rear.png, optional fork.png, meta.json.
Driver: assets/drivers/<id>/head.png, head_crash.png, torso.png, arm.png, leg.png, meta.json.

Meta template:
{"pixelsPerMeter":200,"scale":1,"anchors":{"wheelFront":{"x":150,"y":70},"wheelRear":{"x":-150,"y":70},"driverSeat":{"x":-20,"y":-30},"exhaust":{"x":-200,"y":60},"headlight":{"x":190,"y":-10},"taillight":{"x":-195,"y":-5}}}

How to test:
1. Drop art files into the matching vehicle/driver/map folder.
2. Open the game with ?debug=1.
3. Inspect the physics and sprite alignment.
4. Fix alignment only by editing meta.json.
5. Missing files must never crash the game; the procedural renderer is the fallback.
