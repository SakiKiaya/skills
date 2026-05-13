# v0.5 Semantic Flow Outputs

## operation_flows.json
Higher-level operation records derived from UI events and method calls.

## startup_flow.json
Candidates for application startup sequence, usually Form.Load or Form.Shown.

## risk_points.json
Review targets for threading, timers, and device control.

## ui_backend_flows.json
UI trigger to handler to backend call mapping.

## threading_flows.json
Candidates involving Thread, Task, async/await, Invoke, BackgroundWorker, or timers.

## timer_flows.json
Timer/Tick/Interval candidates.

## device_control_flows.json
Possible PLC, Camera, Vision, Motion, Serial, Socket, LightController, and Database control paths.
