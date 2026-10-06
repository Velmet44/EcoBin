# EcoBin Auto-Segregator Demonstrator

## System Specification

| Document field | Value |
|---|---|
| Document ID | ECO-SYS-SPEC-001 |
| Revision | 0.3 — Single 12 V input; P4 header-powered; design remains draft |
| Status | Draft for project-owner review |
| Date | 2026-10-06 |
| Project | EcoBin |
| Product maturity | Desktop/tabletop proof-of-concept model |
| Primary native CAD tool | FreeCAD; exact version to be recorded when CAD begins |
| Primary controller | Waveshare ESP32-P4-WIFI6-DEV-KIT single-board item; camera purchased separately; no bundled Basic Kit / A / B / C versions |
| Units | mm, g, degrees, V, A, s unless stated otherwise |

> **Scope warning:** This document specifies an educational/functional demonstrator intended to operate under controlled, ideal conditions. It is not a production design, a household appliance release, a safety assessment, or a declaration of Indian regulatory compliance. Where size, loads, thresholds, or part numbers are not yet known, the document identifies them as TBD or provisional rather than claiming they have been validated.

---

## 1. Purpose and project intent

EcoBin is a model of an automatic waste-segregation bin. It demonstrates the complete idea—from placing one object on a tray, through camera-based classification and carousel positioning, to releasing the object into a selected chamber.

The project combines:

1. A fixed, side-mounted input tray and trapdoor.
2. A fixed camera and controlled illumination.
3. A load sensor for item-presence detection.
4. A local image classifier running on an ESP32-P4 development board.
5. Four waste chambers carried by a stepper-indexed rotating base.
6. A servo-actuated trapdoor and gravity-fed drop path.
7. An OLED status display.
8. 3D-printed enclosure, tray, chambers, rotor, brackets, and covers.

The principal demonstration is that a classification result can select one of four physical destinations without manually moving the item from the tray.

### 1.1 Demonstration category mapping

The initial model uses the following demonstration labels:

| Label | Demonstration meaning | Carousel destination |
|---|---|---:|
| A | Recyclable | Position 0 |
| B | Non-recyclable dry / general dry | Position 1 |
| C | Wet / biodegradable | Position 2 |
| D | Unsure / other | Position 3 |

`D` is a fallback destination for an unknown item or a prediction below the configurable confidence threshold. For the model, it is not defined as a safe hazardous-waste container. If hazardous-item imagery is later included in the dataset, the model and demo taxonomy must distinguish an explicit hazardous class from an uncertain prediction.

These labels are for the demonstrator only. A future India-market product would need a separate requirements review against applicable current rules and the selected municipality's collection system. This prototype must not be described as fully implementing the national waste streams.

### 1.2 Intended users and setting

- Project owner/developer operating the demonstrator.
- Classroom, exhibition, or supervised bench demonstration.
- Controlled indoor conditions with a fixed camera, fixed lighting, and known test objects.
- One object placed on the tray per cycle.

### 1.3 Out of scope

The following are explicitly out of scope for this revision:

- Commercial launch, production readiness, long-term life, and field reliability.
- Handling real household waste, fluids, biohazards, batteries, chemicals, sharps, or contaminated items.
- Autonomous recognition of arbitrary waste in arbitrary environments.
- Multi-object separation or object detection in a pile/handful of waste.
- Cloud inference, mobile applications, user accounts, remote telemetry, or online-only operation.
- Compliance certification, formal electrical safety approval, or proof of regulatory conformity.
- Compaction, shredding, washing, drying, deodorizing, or processing waste.
- Quantitative claims about environmental benefit, recycling quality, or field classification accuracy.

---

## 2. Design basis and assumptions

### 2.1 Baseline architecture decisions

| Topic | Baseline decision |
|---|---|
| Number of chambers | Four |
| Chamber motion | All four chambers rotate together on one carousel |
| Indexing | Four indexed positions, nominally 90 degrees apart |
| Tray location | Fixed on the side of the can, above the chamber station path |
| Camera | Fixed to the stationary tray/upper structure; does not rotate with the chambers |
| Object release | Gravity through a short, fixed guide after the trapdoor opens |
| Carousel drive | One stepper motor and one stepper driver; no belt in the baseline design |
| Carousel support | Turntable bearing or equivalent support; motor provides torque, not the sole structural support |
| Position reference | One Hall-effect home sensor and one magnet; subsequent stations tracked by step count |
| Trapdoor actuation | One hobby servo and a simple linkage |
| Controller | One ESP32-P4-WIFI6 development board purchased as a single board item; no separate ESP32-CAM controller |
| Camera interface | Camera module compatible with the selected board's MIPI-CSI connector; OV5647 is the documented starting candidate |
| Inference | On-device using Espressif ESP-DL, with model preparation/quantization performed on a development computer |
| Network use | Optional for development only; the demo classification cycle must work locally |
| Print volume | Every individual printed part must fit within 220 x 220 x 250 mm in its intended print orientation |

### 2.2 Assumptions that must be confirmed before detailed CAD

1. The demonstrator accepts one object per cycle.
2. A person places the object in a repeatable region of the tray.
3. Test objects fit through the trapdoor, guide, and chamber openings.
4. Chamber mouths lie on a common circular path and can each pass beneath the fixed drop station.
5. The tray is already offset to the side, not centered over the carousel axis.
6. The four chambers are model-scale, lightweight, and can be printed separately or as four sectors.
7. The carousel does not need to rotate while the trapdoor is open.
8. The chosen ESP32-P4 board variant has the expected PSRAM, camera connector, and usable GPIOs; verify the exact product SKU before ordering.
9. A compatible camera is acquired separately with the correct CSI ribbon/cable orientation and connector pitch for the selected board revision.
10. Component dimensions, object-size limits, and all enclosure dimensions remain TBD until a packaging layout is established.

### 2.3 Terms

| Term | Meaning |
|---|---|
| Tray | Fixed top-side platform on which a test object is placed |
| Drop station | Fixed side location where the tray outlet, guide, and chamber mouth align |
| Carousel | Rotating carrier that holds all four chambers |
| Chamber | One of the four item-storage compartments on the carousel |
| Home position | Reference angle where the home magnet activates the fixed Hall sensor |
| Index | One nominal 90-degree movement between adjacent chamber positions |
| Gate/trapdoor | Servo-operated flap below the input tray |
| D fallback | Destination used for explicit “other” examples or predictions below the confidence threshold |
| Demo model | The complete controlled-condition physical assembly described in this document |

---

## 3. System architecture

### 3.1 Functional block diagram

```text
       Test item
           |
           v
  Fixed input tray + load cell ------> HX711 ------+
           |                                      |
           v                                      v
  Fixed camera + diffuse light -------------> ESP32-P4
                                                  |
                     +----------------------------+-------------------+
                     |                            |                   |
                     v                            v                   v
              Local image model             Step/dir output      OLED status
                     |                            |
                     v                            v
              Class-to-position map          DRV8825 driver
                                                  |
                                                  v
                                      Stepper + rotating carousel
                                                  |
                                  Hall sensor <--- home magnet
                                                  |
                                                  v
                                     Chamber under drop station
                                                  ^
                                                  |
                      P4 servo PWM -> servo linkage -> trapdoor
```

### 3.2 Physical arrangement

- The upper deck is stationary.
- The tray is mounted on the side of the upper deck, above the drop station.
- The camera and light are mounted to the stationary structure and view the tray.
- The trapdoor is below the tray floor.
- A short stationary guide directs the falling object into the chamber opening at the drop station.
- Four chambers rotate together beneath the stationary drop station.
- A fixed cover/deck prevents an item released at the drop station from falling into a chamber other than the one currently indexed there.
- The carousel rotates around a vertical axis. The chamber openings are positioned so each chamber passes through the same side station.
- The bearing supports axial/radial loads from the carrier. The stepper and hub supply rotation torque.

### 3.3 Coordinate convention

Use a consistent convention in FreeCAD, firmware configuration, and drawings:

- `+Z` is vertically upward.
- The carousel axis is the global Z axis.
- The origin `O_R` is the intersection of the carousel axis and the carousel reference plane.
- The drop station lies at a fixed radius `R_station` from `O_R`.
- Looking down from `+Z`, the selected reference direction is counter-clockwise positive.
- Position 0 places Chamber A beneath the drop station; Positions 1, 2, and 3 place B, C, and D beneath it respectively.
- The exact orientation of the station in the CAD world may be chosen for convenience, then kept unchanged in firmware and drawings.

### 3.4 Carousel geometry requirements

1. All chamber mouths must pass through the same drop station.
2. The nominal angular spacing is 90 degrees.
3. The chamber-mouth centers share the same radial distance from the carousel axis, subject to final CAD dimensions.
4. The drop outlet must overlap the selected chamber opening by enough margin for the chosen test-object envelope.
5. The rotating carrier and chambers must not contact the fixed deck, guide, housing, sensor, or wiring over the full rotation.
6. The four chambers must be retained on the carrier so commanded rotation does not change their relative positions.
7. The chamber placement must be keyed or otherwise unambiguous: A/B/C/D cannot be swapped during assembly without being detected or corrected in the software mapping.
8. A circular rotor is the baseline because it naturally supports four equal angular stations. An octagonal cosmetic enclosure is allowed around it.
9. The baseline design has no belt. A belt may be considered only if a packaging problem is demonstrated, not as an assumed requirement.

### 3.5 Trapdoor and guide

- The trapdoor is closed while the system waits, captures an image, and rotates the carousel.
- The door opens only after the carousel has reached the target position and stopped.
- The guide is fixed and short; it should not move with the carousel.
- The gate must clear the test-object drop path when open.
- The gate must close before carousel movement begins.
- The servo, servo horn, and linkage must not foul the load cell or the moving carousel.
- The tray weighing structure and gate actuation structure should be mechanically separated as far as practical. The load reading is used for presence/stability, not for classifying material.
- Gate open angle, closed angle, open dwell, and close dwell are configuration parameters to be established during bench setup.

---

## 4. Operating sequence

### 4.1 Normal cycle

1. **Power-on:** P4 initializes camera, display, HX711, stepper driver, servo output, and sensor inputs.
2. **Gate-safe initialization:** Firmware commands the trapdoor closed.
3. **Carousel homing:** Stepper moves slowly until the Hall sensor detects the home magnet. Firmware sets carousel index to Position 0.
4. **Ready state:** OLED displays `READY — place one item`.
5. **Presence detection:** Load cell reading changes beyond a configurable presence threshold.
6. **Stability check:** Firmware waits until readings remain within a configurable stability band for a configured window. The baseline window is 500 ms; the allowed weight variation is TBD after sensor calibration.
7. **Image capture:** Camera captures one frame using the fixed lighting and tray backdrop.
8. **Preprocessing:** Firmware converts/resizes the image to the model's required input format and dimensions.
9. **Inference:** Local model returns class scores for A/B/C/D or known classes plus an unknown/fallback result.
10. **Routing decision:** Firmware selects the highest-scoring class if it meets `CONFIDENCE_THRESHOLD`; otherwise it selects D.
11. **User feedback:** OLED displays the predicted class, confidence score, and target chamber while keeping the door closed.
12. **Carousel indexing:** Firmware computes the forward index count from current position to target and commands the stepper. The gate remains closed.
13. **Position settle:** Firmware waits a configurable settling interval after the final step.
14. **Release:** Servo opens the trapdoor for a configured dwell interval. The object falls by gravity through the fixed guide.
15. **Close:** Servo closes the trapdoor. Firmware does not command carousel movement until the close interval has completed.
16. **Clear check:** Load cell returns to its empty-tray tare band. Optional chute beam-break sensor may be used for a more explicit drop event.
17. **Complete:** OLED displays the route and `DONE — ready`.
18. **Next cycle:** System returns to Ready and retains the current carousel index in volatile runtime state.

### 4.2 Startup and reference recovery

- On every power-up or firmware reset, the firmware must home the carousel before accepting a classification cycle.
- If the Hall sensor does not activate within the configured maximum homing travel/time, firmware enters a fault state and does not open the trapdoor.
- The Hall target must identify Position 0 uniquely. The other positions are computed from commanded step counts.
- If power is removed during movement, the next startup re-homes instead of trusting the previous software position.

### 4.3 State machine

| State | Actions | Exit condition |
|---|---|---|
| `BOOT` | Initialize clocks, GPIO, display, camera and drivers | Initialization attempted |
| `SELF_TEST` | Check required peripherals and read sensor status | Pass to HOME; failure to FAULT |
| `HOME` | Close gate and seek Hall home reference | Sensor hit or homing timeout |
| `READY` | Monitor load cell for an item | Presence threshold exceeded |
| `STABILIZE` | Wait for stable tray reading | Stable window reached or timeout |
| `CAPTURE` | Capture one image | Frame captured or camera error |
| `INFER` | Run local model and calculate scores | Prediction available or inference error |
| `INDEX` | Move carousel to target position | Commanded steps complete |
| `SETTLE` | Wait for motion to stop | Dwell elapsed |
| `RELEASE` | Open gate and wait | Open dwell elapsed |
| `CLOSE` | Close gate | Close dwell elapsed |
| `VERIFY_CLEAR` | Confirm tray is empty/tared | Clear, timeout, or fault |
| `COMPLETE` | Display result | Return to READY |
| `FAULT` | Keep/command gate closed, stop motion, display code | Operator reset/power cycle |

### 4.4 Fault behavior

| Fault | Required demo response |
|---|---|
| Camera initialization/capture failure | Keep gate closed; show camera fault; do not index |
| Model/inference error | Keep gate closed; show AI fault; do not index |
| Load cell not stable | Wait to timeout, then request item replacement/retry; no gate opening |
| Home sensor not found | Stop motor command; show homing fault; no gate opening |
| Gate action not completed by dwell | Keep carousel stationary; show gate fault |
| Item remains on tray after release | Do not start the next cycle automatically; show release/clear fault |
| Unexpected reset | On reboot, close gate, re-home, return to READY only after initialization |

These are demonstrator control responses, not safety-rated functions.

---

## 5. Mechanical specification

### 5.1 Main assemblies

1. **Stationary enclosure and frame** — supports the fixed deck, tray, motor, bearing, camera, and electronics.
2. **Fixed input tray assembly** — tray surface, load cell support, and sensor cable routing.
3. **Camera/light assembly** — fixed camera hood, sensor bracket, and diffuse light.
4. **Trapdoor assembly** — flap, hinge, servo bracket, horn/linkage, and fixed drop guide.
5. **Rotating carousel assembly** — carrier, hub, bearing interface, and four retained chambers.
6. **Control/electronics assembly** — P4 board, stepper driver, sensor interfaces, power inputs, OLED, and wiring.
7. **Service access assembly** — removable panel or upper cover that permits chamber and electronics access in the model.

### 5.2 Tray and sensing area

- Tray is stationary and located at the side drop station.
- Camera view must include the full intended object-placement region.
- A visible tray boundary/backdrop should make object placement repeatable.
- The LED source should illuminate the object without directly saturating/glinting the camera.
- The load cell must detect placement without the fixed frame bypassing the measured force path.
- The trapdoor/servo reaction force should not be interpreted as a new item. Firmware uses the stable pre-release reading and ignores readings during door motion.
- Tray surface, door opening, and guide dimensions are TBD and depend on the maximum demonstration-object envelope.

### 5.3 Carousel and support

- One vertical rotary axis.
- Four indexed positions at nominal 90-degree intervals.
- One bearing supports the rotating carrier; a center hub couples it to the stepper.
- The motor mount and bearing seat are stationary and attach to the lower frame.
- A clearance gap is required between rotating chamber tops and the fixed deck/cover. The gap must prevent contact while keeping the drop path constrained.
- Carrier runout, axis clearance, bearing OD, shaft/coupler size, and chamber retention features are TBD until components and enclosure envelope are chosen.
- Baseline housing may be octagonal; the rotor and chamber indexing geometry should remain rotationally symmetric.

### 5.4 Chambers

- Quantity: four.
- Each chamber has an identifying label or molded/printed letter A, B, C, or D.
- All chamber openings must have the same interface geometry at the drop station.
- For the first model, equal chamber volume is acceptable; equal volume is not a real-world capacity recommendation.
- Chambers may be four wedge sectors or four separate bins held in fixed locations on the rotating carrier.
- Baseline service concept: remove the outer access panel/cover and lift the chamber modules out of the carrier.
- Chamber capacity, wall thickness, and exact cross-section are TBD.

### 5.5 Trapdoor

- One hinged flap below the tray.
- Servo controls the opening and closing motion through a horn or simple linkage.
- Closed and open servo angles are firmware configuration values established on the assembled model.
- The flap must not scrape the guide, tray frame, or carousel.
- The flap opening must be larger than the selected maximum test-object cross-section with clearance; exact opening dimensions are TBD.
- The door must be closed before every carousel index command.

### 5.6 Camera placement

- Camera remains fixed relative to the tray.
- Camera is mounted in a side pod/hood, looking into the tray at a fixed distance and angle.
- Exact focus distance, camera angle, and field of view are TBD after a physical camera test.
- Use the board-compatible OV5647 CSI camera as the single-camera baseline.
- The camera pod should hold the camera and LED diffuser without placing the lens or cable in the trapdoor/chamber sweep envelope.

---

## 6. Electronics and power specification

### 6.1 Controller and camera

- Main board: Waveshare ESP32-P4-WIFI6-DEV-KIT single-board item (Robu seller reference R255962 is the board-only candidate; confirm exact revision and package contents before ordering).
- Camera: separately purchased compatible MIPI-CSI module; OV5647 is the documented starting candidate.
- Do not add a separate ESP32-CAM controller in the baseline architecture.
- Use the P4 for image capture coordination, local inference, state machine, OLED, load cell, Hall sensor, stepper control, and servo control.
- The board's ESP32-C6 connectivity companion is not needed for normal classification. Wi-Fi may be used for development/debugging only; loss of network must not prevent a local demo cycle.
- Confirm the exact camera variant, flex cable direction, connector pitch, and board revision before ordering.

### 6.2 Firmware platform and model runtime

- Baseline firmware framework: ESP-IDF.
- Baseline inference framework: Espressif ESP-DL, with a model converted/quantized into the supported deployment format (`.espdl`).
- Model training/initial conversion occurs on a development computer; inference occurs on the P4.
- Pin and record the ESP-IDF, ESP-DL, compiler, model-conversion tool, and camera-driver versions when implementation begins.
- The exact supported model operators must be checked against Espressif's operator-support reference before model training is finalized.

### 6.3 Sensor and actuator interfaces

| Device | Interface | Notes |
|---|---|---|
| Load cell | Wheatstone bridge to HX711; HX711 digital output to P4 GPIO | Calibrate tare and stable band on the assembled tray |
| Hall sensor | Digital GPIO input | Used for carousel home reference |
| Stepper driver | STEP, DIR, ENABLE GPIO outputs | Driver power/current set to selected motor datasheet |
| Servo | PWM-capable output | Servo has a dedicated 5 V supply rail |
| OLED | I²C | Use board pins confirmed free in the exact single-board schematic |
| LED | 5 V supply with suitable switch/driver if GPIO-controlled | Do not power a high-current light directly from a GPIO |
| Optional drop sensor | IR break-beam digital input | Optional; not required for the first model |

All GPIO assignments remain TBD until the exact P4 board schematic and reserved camera/SDIO/display pins are reviewed. Do not assume arbitrary exposed header pins are unused.

### 6.4 Power rails

Baseline power partition (single 12 V mains input for the whole demonstrator):

- 12 V adapter input: one enclosed 12 V / 5 A adapter feeds a fused, switched low-voltage distribution block.
- Stepper motor/driver: direct 12 V branch to the DRV8825 carrier, sized for the exact NEMA-17 and driver current.
- Servo: separate LM2596 buck branch set to 5.0 V (SERVO module), sized for its transient current.
- P4 board and low-current electronics: separate LM2596 buck branch set to 5.0 V (LOGIC module) feeding the P4 40-pin header `VCC_5V` and `GND` only; never `ESP_3V3` or `VBUS_OUT`. USB-C is used for flashing/debug data only, and USB power must never be connected while the header rail is powered.
- Sensor/light rails: use the correct module voltage; avoid powering the discrete LEDs or servo from a GPIO.
- Establish a common star ground between P4, motor driver, and both buck outputs where required for control signals, while keeping motor current paths away from low-level sensor wiring.
- Add a master power switch, an inline fuse, and a clearly accessible power connector to the model.
- Final supply current ratings depend on the exact motor, servo, LED, and board variants; re-verify the 12 V 5 A adequacy against measured motor current.

---

## 7. Firmware and control requirements

### 7.1 Functional requirements

| ID | Requirement |
|---|---|
| FW-001 | Firmware shall initialize the camera, display, load cell, Hall input, stepper driver, and servo output. |
| FW-002 | Firmware shall command the trapdoor closed during startup and before carousel homing. |
| FW-003 | Firmware shall home the carousel before accepting a new item after every reset/power-up. |
| FW-004 | Firmware shall detect a tray load change and require a stable reading before camera capture. |
| FW-005 | Firmware shall capture one image per accepted item cycle. |
| FW-006 | Firmware shall run inference locally without requiring Wi-Fi or cloud access. |
| FW-007 | Firmware shall map the prediction to one of four chamber indexes. |
| FW-008 | A prediction below `CONFIDENCE_THRESHOLD` shall route to Position 3 / D. |
| FW-009 | Firmware shall not move the carousel while the trapdoor is commanded open. |
| FW-010 | Firmware shall not open the trapdoor until indexing is complete and the settling delay has elapsed. |
| FW-011 | Firmware shall close the trapdoor before accepting the next cycle. |
| FW-012 | Firmware shall display at least the selected class/chamber and current state. |
| FW-013 | Firmware shall display fault states and block normal operation after a critical demo error. |
| FW-014 | Firmware shall expose service/test commands that allow selecting each chamber without AI inference. |
| FW-015 | Class-to-position mapping, stepper steps/revolution, microstep setting, servo endpoints, stability band, and confidence threshold shall be configurable. |

### 7.2 Carousel indexing logic

- Position identifiers are integers `0..3` corresponding to A..D.
- Home is Position 0.
- At startup, seek the Hall sensor at low speed; once detected, set the software position to 0.
- Compute forward index count as `(target - current + 4) mod 4`.
- Rotate forward by that number of quarter-turns. Maximum commanded movement is three indexes.
- After the commanded steps, wait for `ROTATION_SETTLE_MS` before opening the gate.
- The step count uses motor steps/revolution and driver microstep configuration, not hard-coded assumed pulses.
- Optional acceleration ramps may be used, but speed and acceleration are demo configuration values.
- If the motor is changed, update and revalidate steps/revolution, microstep configuration, and homing direction.

### 7.3 Confidence and routing

- Model output must include a predicted label and a score.
- Initial demo threshold: `CONFIDENCE_THRESHOLD = 0.60` as a provisional configuration value, not a validated probability guarantee.
- If the top score is below the threshold, route to D.
- D may also be trained with representative “other” objects. A low score from A/B/C still overrides the predicted route and selects D.
- Display score as a model score; do not represent it as a calibrated real-world probability unless calibration has been performed.
- The threshold must be tuned using held-out examples and recorded in firmware configuration.

### 7.4 Timing parameters

The following values are to be set through configuration and tuned on the assembled model:

| Parameter | Initial value/status |
|---|---|
| `LOAD_PRESENT_THRESHOLD` | TBD after HX711/tray calibration |
| `LOAD_STABLE_WINDOW_MS` | 500 ms initial baseline |
| `LOAD_STABLE_BAND` | TBD after noise measurement |
| `CAMERA_SETTLE_MS` | TBD after capture testing |
| `HOMING_SPEED` | Low-speed configuration TBD |
| `HOMING_TIMEOUT_MS` | TBD based on full carousel travel |
| `ROTATION_SETTLE_MS` | TBD after motion test |
| `GATE_OPEN_ANGLE` | Calibrate on assembled trapdoor |
| `GATE_CLOSED_ANGLE` | Calibrate on assembled trapdoor |
| `GATE_OPEN_DWELL_MS` | TBD after gravity-drop test |
| `GATE_CLOSE_DWELL_MS` | TBD after servo test |
| `RELEASE_TIMEOUT_MS` | TBD; used to detect an item remaining on tray |
| `CONFIDENCE_THRESHOLD` | 0.60 provisional; tune on held-out dataset |

---

## 8. AI, dataset, and image pipeline

### 8.1 First-version model

- Task: single-image classification of one item on the tray.
- Initial destinations: A, B, C, D/Other.
- Model is trained on a computer and deployed to the P4 in ESP-DL format.
- No object detection is required for the first version.
- Do not process multiple items in a single image as separate objects in this revision.

### 8.2 Data collection assumptions

- Capture images with the final demo camera, background, lighting, camera distance, and tray placement.
- Record class label, capture session, physical object identity, lighting setup, and image preprocessing configuration.
- Include multiple physical examples per class; avoid relying on many nearly identical frames of one object.
- Keep a held-out test set separated by object instance or capture session, not just a random frame-level split.
- Only use images the project owner has permission to use. Keep dataset source and usage notes with the dataset manifest.
- Raw image storage policy and Git LFS/large-file approach are TBD. Do not silently commit a large or externally restricted dataset.

### 8.3 Preprocessing and inference

1. Capture a frame after load stability is reached.
2. Crop/resize the tray region to the model input dimensions.
3. Apply the same color order, normalization, and quantization expected by the model.
4. Run ESP-DL inference.
5. Convert scores into a route using the configured class mapping and confidence rule.
6. Return route, score, model identifier, and an inference status to the state machine.

Input resolution, pixel format, normalization, model topology, quantization, model size, RAM allocation, and latency are TBD until the dataset/model baseline is tested on the chosen board.

### 8.4 Evaluation

The demonstrator must report:

- Held-out test accuracy and a confusion matrix.
- Per-class count, correct count, and recall for A/B/C/D or the selected model labels.
- Number of samples routed to D by the confidence rule.
- Inference time and peak memory/logged allocation as available from the framework.
- End-to-end route correctness separately from model classification correctness.

Proposed initial demo target: at least 90% correct on a fixed, controlled, held-out test set, with class-specific results reported. This is a project target, not achieved evidence. The dataset size and acceptance set must be defined before declaring the target passed.

---

## 9. User interface and status behavior

### 9.1 OLED messages

Minimum states to display:

- `STARTING`
- `HOMING`
- `READY — PLACE ONE ITEM`
- `WAIT — HOLD STILL`
- `ANALYZING`
- `A / B / C / D — MOVING`
- `D — LOW CONFIDENCE / OTHER`
- `RELEASING`
- `DONE — REMOVE ITEM`
- `FAULT — <code>`

Exact wording and symbols may change for the exhibit/demo. The screen is informational, not a control safety device.

### 9.2 User interaction assumptions

- The operator places one known test object on the tray and removes hands before the automated cycle begins.
- The initial version does not need a motorized user lid.
- A local test button or serial command may trigger a service cycle for each chamber.
- The demo should make the selected chamber visible enough to observe, either by using a transparent body, an inspection window, or a camera/rendered cutaway in presentation material.

---

## 10. BOM baseline

The sourced, itemized cost and procurement snapshot is maintained in `docs/bom/EcoBin-Demonstrator-BOM.csv`; this specification remains cost-independent. The BOM uses separate order lines and excludes preassembled project bundles. A priced candidate is not automatically a fit-approved component: unresolved electrical and mechanical checks remain open until the wiring diagram and CAD packaging are complete.

### 10.1 Purchased electronics and motion parts

| Qty. | Part | Baseline specification | Status |
|---:|---|---|---|
| 1 | ESP32-P4-WIFI6-DEV-KIT single-board item | Waveshare P4/C6 board; Robu seller reference R255962 is the current board-only candidate | Confirm exact revision, package contents, price, and stock; do not purchase Waveshare bundled Basic Kit / A / B / C versions |
| 1 | MIPI-CSI camera module | Waveshare RPi Camera (B), OV5647, standalone camera listing | Candidate; confirm P4 sensor-driver support, cable orientation, connector pitch, and board revision before ordering; camera package includes its own flex leads |
| 1 | Single-point load cell | 5 kg nominal capacity; standalone product | Matches the spec baseline; confirm mounting span and demonstration-object mass range in CAD |
| 1 | HX711 board | Standalone load-cell ADC/interface module | Purchase separately from the load cell |
| 1 | NEMA-17 stepper | Robocraze 17HS8401S candidate; four-wire bipolar if confirmed | Provisional; seller listing does not expose rated phase current; verify current and step angle before pairing with a driver |
| 1 | DRV8825 carrier | STEP/DIR driver candidate | Provisional; set current and provide cooling per exact carrier and motor documentation |
| 1 | MG90S micro servo | Robocraze 180° trapdoor actuator candidate | Verify torque, endpoints, and linkage travel against the printed flap |
| 1 | Hall-effect sensor module | A3144EUA open-collector module candidate | Use a 3.3 V signal pull-up for the P4 GPIO; verify module supply/output details because seller copy is inconsistent |
| 1 | Neodymium disc magnet | Probots 5 × 3 mm candidate | Verify sensor trigger distance and printed retention before finalizing |
| 1 | I²C OLED | Robocraze 1.3-inch 128 × 64 candidate | Controller IC remains TBD; confirm driver/library compatibility before ordering |
| 1 pack each | White LEDs and current-limit resistors | Robocraze 5 mm white LED pack of 10 and 220 Ω resistor pack of 10 | Separate commodity component packs; emitter count, current, and printed diffuser performance TBD after camera testing |
| 1 | 12 V DC supply (single mains input) | Robocraze 12 V / 5 A enclosed adapter candidate | Confirm barrel size/polarity and adequacy against measured motor plus both buck loads |
| 1 | Regulated 5 V logic supply | Second LM2596 buck module (LOGIC) from the 12 V rail, feeding P4 header VCC_5V/GND | Adjust to 5.0 V and verify with a meter before connecting; never connect USB-C power while header-powered |
| 1 | Regulated 5 V servo supply | First LM2596 buck module (SERVO) from the 12 V rail | Adjust and verify with a meter before attaching the servo; size against measured servo transient load; label both buck modules |
| 1 optional | IR break-beam pair | Detect item clearing the guide | Optional for first build |
| As needed | Headers, connectors, 12 V distribution block, wires, heat-shrink, switch, fuse, standoffs | Interconnect, single-input distribution, and mounting | Exact quantities after wiring diagram |

### 10.2 Non-printed mechanical hardware

| Qty. | Part | Purpose |
|---:|---|---|
| 1 | Turntable bearing | Supports rotating carrier |
| 1 | Motor-to-carousel hub/coupler | Transfers motor torque to carrier |
| As needed | M3 screws, nuts, washers, and spacers | Joins printed modules and mounts boards |
| As needed | Hinge pin, shoulder screw, or small metal pin | Trapdoor pivot |
| As needed | Board standoffs and camera fasteners | Mounts electronic modules |
| As needed | Cable ties or reusable cable restraints | Keeps wiring clear of moving parts |

### 10.3 3D-printed parts register

Every individual print must fit the printer envelope in the intended orientation. Design target is 210 x 210 x 240 mm maximum per part, with the absolute limit 220 x 220 x 250 mm.

| Part ID | Printed part | Qty. | Split/assembly rule |
|---|---|---:|---|
| PR-001 | Lower chassis/base frame | 1 assembly | Print as one if within envelope; otherwise split into 2–4 keyed panels/segments and bolt together |
| PR-002 | Outer enclosure side panels | 4 or more | Separate flat/curved panels; split vertically if any panel exceeds 250 mm height |
| PR-003 | Fixed upper deck/top plate | 1 assembly | Split into 2 or 4 keyed sections if larger than target footprint |
| PR-004 | Fixed drop-station collar/guide | 1 | One short part preferred; split upper/lower if over height limit |
| PR-005 | Input tray body | 1 | One piece if within envelope; otherwise split into keyed halves with underside fasteners |
| PR-006 | Tray/load-cell support frame | 1 | Separate from trapdoor bracket so door forces do not load the scale structure unnecessarily |
| PR-007 | Trapdoor flap | 1 | Separate moving part; include pivot features and servo/linkage clearance |
| PR-008 | Trapdoor hinge supports | 2 | Separate left/right blocks or one bridge if it fits |
| PR-009 | Servo mount | 1 | Include slots or adjustment features for linkage calibration |
| PR-010 | Servo linkage/horn adapter | 1 | Small replaceable part; do not rely on printed flex as the hinge |
| PR-011 | Carousel carrier plate | 1 assembly | Print in 1 piece if it fits; otherwise 4 keyed quadrants with bolted joints and a center hub interface |
| PR-012 | Center hub/spider | 1 | Interfaces carrier to motor coupler; bolt to carrier, not adhesive only |
| PR-013 | Bearing seat/retainer | 1 assembly | Split into two or four retainer segments if needed for installation/service |
| PR-014 | Chamber A | 1 | One removable container/sector; split vertically if height exceeds 250 mm |
| PR-015 | Chamber B | 1 | Same locating/opening interface as A |
| PR-016 | Chamber C | 1 | Same locating/opening interface as A |
| PR-017 | Chamber D | 1 | Same locating/opening interface as A |
| PR-018 | Chamber retention clips/rails | 4 or more | Prevent chamber movement on carrier; removable for service |
| PR-019 | Stepper motor bracket | 1 | Mounts motor below carrier/bearing plane; leave shaft/coupler access |
| PR-020 | Camera hood/bracket | 1 assembly | Fixed to stationary tray structure; must not rotate with carousel |
| PR-021 | Camera bezel/lens guard | 1 | Keeps camera position repeatable and protects lens from accidental contact in demo |
| PR-022 | LED diffuser/light ring carrier | 1 | Holds the light around/near camera view without obscuring the image |
| PR-023 | Hall-sensor bracket | 1 | Fixed sensor location with adjustment slots during calibration |
| PR-024 | Magnet holder | 1 | Attaches magnet to carousel at the home target |
| PR-025 | OLED bezel/display mount | 1 | Mounts display on visible enclosure face |
| PR-026 | Removable service/access panel | 1 or more | Gives access to chambers, motor, and wiring; retention method TBD |
| PR-027 | Bottom motor/rotor cover | 1 assembly | Split if larger than print envelope; avoid covering bearing/fastener access permanently |
| PR-028 | Feet/pads | 4 | Printed feet or pads; non-slip inserts may be added if desired |
| PR-029 | Cable guides/clips | 6–12 | Route stationary wiring away from rotor and hinge sweep |
| PR-030 | Optional beam-break sensor brackets | 2 | Only if the optional drop-confirmation sensor is used |

The main carrier and chamber modules should be designed as separate FreeCAD parts/objects even if the first version uses a unified print. This permits chamber replacement and independent iteration. If the complete circular carrier exceeds the bed size, split the carrier into keyed quadrants; if individual chamber sectors exceed the bed, split them into lower container bodies and upper rim extensions. Do not create a single print that exceeds the specified printer envelope.

---

## 11. 3D printing and CAD rules

### 11.1 Printer envelope

- Maximum individual print envelope: 220 x 220 x 250 mm.
- Preferred design envelope: 210 x 210 x 240 mm.
- Envelope applies after selecting print orientation, not just to the part's default FreeCAD bounding box.
- Every assembly made of multiple prints may exceed the individual print envelope.
- Store split parts as separate FreeCAD objects/files and identify how they assemble.

### 11.2 Materials and process

- PLA/PLA+ is acceptable for the controlled indoor demonstrator unless part flexibility/temperature requires another material.
- No food-contact, liquid containment, sanitation, UV, or outdoor performance claim is made.
- Exact material, printer profile, layer height, infill, perimeters, supports, and orientation should be recorded when printing begins.
- Use a consistent orientation and material across mating parts where possible.

### 11.3 Assembly features

- Prefer screws, nuts, captive slots, or heat-set inserts for parts that will be opened repeatedly.
- Use alignment keys/dowels on split large plates and panels.
- Carrier quadrant joints must be positively located and fastened; adhesive alone is not the baseline structural joint.
- Preserve access to bearing fasteners, motor coupler, servo adjustment, Hall sensor, and camera cable.
- Design serviceable electronic mounts; do not permanently bury the P4 board or driver inside a sealed print.
- Add chamfers/lead-ins at chamber locating interfaces to ease assembly.

### 11.4 CAD model organization

- Create separate definitions for the stationary frame, tray, trapdoor, chute, camera/light mount, carousel, each chamber, motor bracket, and sensor mounts.
- Use stable names such as `BaseFrame`, `TopDeck`, `InputTray`, `Trapdoor`, `DropGuide`, `Carousel`, `Chamber_A`, `Chamber_B`, `Chamber_C`, `Chamber_D`, `CameraMount`, and `StepperMount`.
- Establish the rotary axis and drop-station reference as datum geometry before detailed features.
- Use named parameters for overall envelope, rotor diameter, station radius, chamber spacing, tray opening, chamber opening, and print segmentation.
- Keep imported electronics and purchased components separate from printed components.
- Record the exact FreeCAD version and document units when CAD work begins.

---

## 12. Verification and demo acceptance plan

Testing is for a controlled model, not production qualification.

### 12.1 Mechanical bench tests

| Test ID | Test | Pass condition |
|---|---|---|
| ME-001 | Rotate carrier through all four indexes by service command | Every chamber is brought beneath the drop station without collision |
| ME-002 | Home sensor repeatability | Repeated home cycles return the carrier to the same usable alignment |
| ME-003 | Trapdoor movement without carousel | Door opens/closes through configured endpoints without binding |
| ME-004 | Carousel movement with door closed | No contact between door, fixed guide, deck, chambers, or carrier |
| ME-005 | Gravity drop test | A representative test object clears the tray and enters the selected chamber |
| ME-006 | Access/assembly test | Chambers can be installed/removed using the intended panel/cover access |
| ME-007 | Print envelope inspection | Every printed component's oriented bounding box is within 220 x 220 x 250 mm |

### 12.2 Electronics/firmware tests

| Test ID | Test | Pass condition |
|---|---|---|
| EL-001 | Power-on/reset | Board initializes and homes before showing READY |
| EL-002 | Load cell | Empty tare is stable and a placed item crosses the configurable presence threshold |
| EL-003 | Hall home | Sensor transitions are detected and position 0 is set |
| EL-004 | Stepper driver | Four positions can be selected by service command without missed steps during the defined demonstration test |
| EL-005 | Gate servo | Firmware opens and closes the flap using calibrated endpoints |
| EL-006 | Interlock logic | Stepper is not commanded while the gate is open; gate does not open before index completion |
| EL-007 | OLED | All normal states and injected faults display readable text |
| EL-008 | Offline behavior | Classification/demo routing works with Wi-Fi disconnected |

### 12.3 AI and end-to-end tests

- Freeze and identify a demo test set before reporting model accuracy.
- Keep test objects separate from training images where possible.
- Record class mapping, model version, confidence threshold, image preprocessing, and result for each sample.
- Report model correctness separately from physical route correctness.
- Proposed mechanical integration test: 10 commanded cycles for each chamber (40 total) using service-selected destinations; target 40/40 correct drops under controlled conditions.
- Proposed initial classifier target: at least 90% on the fixed held-out controlled-condition dataset, with a confusion matrix and per-class counts. This target is provisional until the dataset is defined.
- Test low-score predictions and confirm that they route to D.
- Test empty tray/no item and confirm no automatic gate opening or carousel movement occurs.

### 12.4 Demonstration acceptance

The demonstrator is considered ready for a project presentation when:

1. All four chamber positions can be homed and indexed.
2. The tray detects a placed object and captures a repeatable image.
3. The local classifier returns a displayable result or D fallback.
4. The carousel selects the correct chamber from a software test command.
5. The trapdoor opens only after the target index and drops the item by gravity.
6. The door closes and the system returns to READY.
7. The planned 40-cycle mechanical routing test passes or any failures are recorded and corrected.
8. The CAD/print assembly and electronics BOM reflect the built demonstrator revision.

---

## 13. Project work packages

### WP-0 — Resolve blocking layout values

Decide outer diameter/width, overall height, chamber dimensions, tray dimensions, maximum object envelope/mass, and the drop-station radius. These values govern nearly every printed part.

### WP-1 — System layout and packaging

Create a dimensioned top and side layout with the fixed side tray, carousel axis, station radius, chamber locations, top deck, bearing, motor, and service access. Confirm the chamber mouths pass under the station.

### WP-2 — Motion-only prototype

Build the frame, bearing, carrier, motor mount, Hall home sensor, and four chamber placeholders. Test homing and 90-degree indexing before adding AI or the trapdoor.

### WP-3 — Tray, load cell, and trapdoor prototype

Build the fixed tray, separate scale support, gate flap, servo bracket/linkage, and short drop guide. Verify clearance and gravity release.

### WP-4 — Camera and P4 bring-up

Confirm exact board/camera compatibility, camera capture, fixed illumination, OLED, HX711, Hall sensor, stepper driver, and servo I/O using the selected P4 board.

### WP-5 — Model pipeline

Capture/label the controlled dataset, train a four-class/known-class classifier on a computer, convert/quantize it for ESP-DL, deploy to P4, and record accuracy/latency.

### WP-6 — Firmware integration

Implement the specified state machine, class mapping, homing/indexing, gate control, display states, service commands, and fault handling.

### WP-7 — Integrated demo and revision record

Run acceptance tests, record failures/fixes, capture photos/renders, identify the final demo BOM and software/model versions, and update this specification revision.

---

## 14. Repository organization

This specification is stored at `docs/specs/EcoBin-Demonstrator-System-Specification.md`.

| Repository path | Intended project content |
|---|---|
| `3D-Design/parts/` | Individual native FreeCAD part files |
| `3D-Design/assemblies/` | Top assembly and subassemblies |
| `3D-Design/exports/` | Controlled STEP/STL/3MF/PDF exports |
| `firmware/src/` | Firmware source and state-machine implementation |
| `firmware/include/` | Pin map, parameters, class map, configuration headers |
| `firmware/lib/` | Project-owned firmware libraries/adapters |
| `firmware/test/` | Firmware unit/integration test code and logs |
| `ai-model/datasets/` | Dataset manifests and approved demo images; large files policy TBD |
| `ai-model/training/` | Training scripts, configs, and experiment notes |
| `ai-model/exports/` | P4 deployable model artifacts and checksums |
| `ai-model/evaluation/` | Confusion matrices, metrics, and held-out test results |
| `electronics/schematics/` | Controller, power, and interface diagrams |
| `electronics/pcb/` | Any custom PCB source if introduced later |
| `electronics/wiring-diagrams/` | Point-to-point prototype wiring and pin map |
| `electronics/datasheets/` | Datasheets for exact selected purchased parts |
| `docs/specs/` | Controlled specifications and requirement revisions |
| `docs/research/` | Research notes and source links |
| `docs/images/` | Spec diagrams and annotated reference images |
| `media/photos/` | Build/test photos |
| `media/renders/` | CAD renders and presentation images |
| `media/videos/` | Demo video captures |
| `scripts/` | Data/CAD utility scripts and validation helpers |

Large datasets, model binaries, and video should be tracked with Git LFS or another documented artifact strategy if they exceed normal Git use. Preserve dataset/model manifests and hashes. Do not commit credentials, access tokens, or private keys. Keep development-environment/tooling content distinct from EcoBin product deliverables; review the existing `.agents/` directory's repository scope separately.

---

## 15. Open decisions and assumptions register

| ID | Decision/question | Priority | Current status |
|---|---|---|---|
| OI-001 | What are the overall width/diameter and height of the model? | Blocking for detailed CAD | TBD |
| OI-002 | What are the maximum test-item dimensions and mass? | Blocking for tray/gate/chute | TBD |
| OI-003 | What chamber volume and shape should be used? | High | TBD; equal model chambers are acceptable initially |
| OI-004 | Are the chambers four wedge sectors or four separate containers on the carrier? | High | TBD |
| OI-005 | What exact board-only P4 SKU/revision is being purchased, and are its package contents confirmed to be a single board rather than a bundled version? | Blocking for electronics wiring | Robu ref R255962 is the board-only candidate; current price/package contents require reconfirmation |
| OI-006 | What exact compatible OV5647 CSI camera module/cable will be used? | Blocking for camera integration | Waveshare RPi Camera (B) SKU 8193 is a separate candidate; P4 driver/connector compatibility remains to be verified |
| OI-007 | What exact NEMA-17 stepper current/step angle and DRV8825 carrier are selected? | High | Robocraze 17HS8401S and DRV8825 are price candidates; seller listing omits motor phase current, so do not order until matched |
| OI-008 | What is the trapdoor aperture size, flap travel, and servo mounting arrangement? | High | TBD after object envelope |
| OI-009 | What are the tray dimensions and load-cell mounting span? | High | TBD |
| OI-010 | What is the controlled dataset and fixed held-out test set? | High for AI acceptance | TBD |
| OI-011 | Is D trained as an explicit Other class in addition to score-threshold fallback? | Medium | Baseline: yes if examples are available; otherwise low-score routes to D |
| OI-012 | Is the proposed 0.60 confidence threshold suitable for the selected model? | Medium | Provisional; tune using held-out data |
| OI-013 | What is the maximum acceptable demo cycle time? | Medium | TBD |
| OI-014 | What access-panel strategy permits chamber replacement? | Medium | Baseline: removable panel/top cover |
| OI-015 | Should an optional chute break-beam sensor be included? | Low | Not in first BOM baseline |
| OI-016 | Which filament and printer profile will be used? | Medium | eSun 1.75 mm PLA+ cold-white is a candidate; exact profile and spool count depend on printer and slicer output |
| OI-017 | What is the raw-dataset/model artifact versioning policy? | Medium | TBD before dataset ingestion |

### 15.1 Items that must be decided before detailed CAD

At minimum, resolve OI-001 through OI-009 sufficiently to make a layout and fit the chosen purchased components. AI data/model decisions can proceed in parallel, but final inference performance cannot be claimed before deployment testing on the selected board.

---

## 16. Known risks and mitigations for this model

| Risk | Effect on demo | Mitigation |
|---|---|---|
| Chamber mouth does not align with the side drop station | Item lands on the deck or wrong chamber | Establish station radius and 90-degree pattern as master layout datums |
| Carousel binding or missed steps | Wrong chamber reaches the tray | Support carrier on bearing, reduce acceleration, home on startup, verify 40-cycle routing |
| Tray scale is affected by servo/linkage forces | False presence/unstable reading | Separate scale support from gate support; freeze weight processing during motion |
| Camera connector/sensor mismatch | No image capture | Use a board-compatible CSI camera; verify exact board revision, sensor driver, and cable before ordering |
| Poor lighting/background variability | Classifier errors | Fixed camera mount, diffuse light, repeatable tray background and item placement |
| Model confidence appears high on unknown inputs | Wrong destination | Use D fallback threshold; include unknown examples; report model limitations |
| 3D printed carrier joint loosens | Chamber position drifts | Keyed joints, through-bolts, carrier alignment test, inspect before demo |
| Large part exceeds printer envelope | Part cannot be fabricated | Maintain 210 x 210 x 240 mm target and split oversized parts at planned joints |
| Power rail disturbance during motor/servo movement | P4 reset or corrupt sensor read | Separate motor/servo power rails; common signal ground; test with motor active |

---

## 17. Change control

- Rev 0.3 moves the whole demonstrator to a single 12 V input with separate SERVO/LOGIC bucks and header-powered P4; it does not close the motor-current, barrel/switch/fuse selection, or wiring-diagram validation actions.
- The project owner approves changes to chamber labels, hardware baseline, camera interface, motor architecture, or print-envelope rule.
- Changes to class mapping must update firmware configuration, model labels, display text, and this specification.
- Changes to carousel diameter, station radius, chamber openings, bearing, or motor mount require a fresh collision/alignment review.
- Changes to the camera, lighting, tray background, or image preprocessing invalidate prior AI evaluation results until the test set is rerun.
- Changes to the P4 board SKU/revision or CSI camera require schematic/connector and firmware-driver review.
- Increment document revision when a baseline requirement or architecture decision changes; keep the previous Git history for traceability.

---

## 18. Reference documentation

These sources support the selected development-board and model-runtime baseline. Confirm the exact hardware revision and software versions during implementation.

1. Waveshare, [ESP32-P4-WIFI6-DEV-KIT documentation](https://docs.waveshare.com/ESP32-P4-WIFI6-DEV-KIT) — board architecture, camera interface, memory, and development notes.
2. Espressif, [ESP32-P4 overview](https://www.espressif.com/en/products/socs/esp32-p4) — P4 capabilities and connectivity architecture.
3. Espressif, [ESP-DL Getting Started](https://docs.espressif.com/projects/esp-dl/en/latest/getting_started/readme.html) — supported P4 target, ESP-IDF basis, model quantization and deployment flow.
4. Government of India, [Solid Waste Management Rules 2026 summary](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2219676&reg=3&lang=1) — future product-context reference only; this demonstrator does not claim compliance.

---

## 19. Specification approval

This document is a detailed draft baseline. It becomes the implementation baseline when the project owner reviews the open-decision register and accepts the architecture, class mapping, and model acceptance targets.

| Role | Name | Approval/date |
|---|---|---|
| Project owner | TBD | TBD |
| Mechanical design | TBD | TBD |
| Electronics/firmware | TBD | TBD |
| AI/model evaluation | TBD | TBD |
