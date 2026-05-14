# 08 External Dependencies

## External / Project Dependency Chunks

| Chunk ID | Title | Summary | Sources |
|---|---|---|---|
| 0000_System_References | Dependency Group: System References | Aggregated framework references from System.* assemblies. | VbLargeFileDocTest.vbproj |
| external_0000_PLC | External Dependency: PLC | External dependency candidate chunk. | N/A |
| external_0001_Camera_SDK | External Dependency: Camera SDK | External dependency candidate chunk. | N/A |
| external_0002_Vision_SDK | External Dependency: Vision SDK | External dependency candidate chunk. | N/A |

## Dependency Details


### [Dependency Group: System References](chunks/dependencies/0000_System_References.md)

# Dependency Group: System References

| Field | Value |
|---|---|
| dependency_group | System References |
| count | 2 |
| dependencies | [{'type': 'Reference', 'project': 'VbLargeFileDocTest', 'target': 'System.Windows.Forms', 'source': 'VbLargeFileDocTest.vbproj'}, {'type': 'Reference', 'project': 'VbLargeFileDocTest', 'target': 'System.Configuration', 'source': 'VbLargeFileDocTest.vbproj'}] |

## Maintenance Notes

- 確認版本、部署路徑、x86/x64 相容性。
- 若為 SDK / COM / Native DLL，需確認 runtime 與授權。


### [External Dependency: PLC](chunks/dependencies/external_0000_PLC.md)

# External Dependency: PLC

| Field | Value |
|---|---|
| dependency_type | PLC |
| matched_keywords | ['plc'] |
| purpose | External integration candidate 推測 |
| risk | Initialization, deployment, license, architecture, or runtime failure risk 推測 |
| confidence | 0.55 |

## Maintenance Notes

- 確認版本、部署路徑、x86/x64 相容性。
- 若為 SDK / COM / Native DLL，需確認 runtime 與授權。


### [External Dependency: Camera SDK](chunks/dependencies/external_0001_Camera_SDK.md)

# External Dependency: Camera SDK

| Field | Value |
|---|---|
| dependency_type | Camera SDK |
| matched_keywords | ['camera', 'capture'] |
| purpose | External integration candidate 推測 |
| risk | Initialization, deployment, license, architecture, or runtime failure risk 推測 |
| confidence | 0.65 |

## Maintenance Notes

- 確認版本、部署路徑、x86/x64 相容性。
- 若為 SDK / COM / Native DLL，需確認 runtime 與授權。


### [External Dependency: Vision SDK](chunks/dependencies/external_0002_Vision_SDK.md)

# External Dependency: Vision SDK

| Field | Value |
|---|---|
| dependency_type | Vision SDK |
| matched_keywords | ['inspect'] |
| purpose | External integration candidate 推測 |
| risk | Initialization, deployment, license, architecture, or runtime failure risk 推測 |
| confidence | 0.55 |

## Maintenance Notes

- 確認版本、部署路徑、x86/x64 相容性。
- 若為 SDK / COM / Native DLL，需確認 runtime 與授權。

