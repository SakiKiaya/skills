# 03 Project Dependencies

## Dependency Chunk Index

| Chunk ID | Title | Summary | Source Refs | Related |
|---|---|---|---|---|
| 0000_VbLargeFileDocTest_System.Windows.Forms | Dependency: VbLargeFileDocTest -> System.Windows.Forms | Dependency chunk. | VbLargeFileDocTest.vbproj | N/A |
| 0001_VbLargeFileDocTest_System.Configuration | Dependency: VbLargeFileDocTest -> System.Configuration | Dependency chunk. | VbLargeFileDocTest.vbproj | N/A |
| external_0000_PLC | External Dependency: PLC | External dependency candidate chunk. | N/A | N/A |
| external_0001_Camera_SDK | External Dependency: Camera SDK | External dependency candidate chunk. | N/A | N/A |
| external_0002_Vision_SDK | External Dependency: Vision SDK | External dependency candidate chunk. | N/A | N/A |
| external_0003_Reference | External Dependency: Reference | External dependency candidate chunk. | N/A | N/A |
| external_0004_Reference | External Dependency: Reference | External dependency candidate chunk. | N/A | N/A |

## Dependency Details


### [Dependency: VbLargeFileDocTest -> System.Windows.Forms](chunks/dependencies/0000_VbLargeFileDocTest_System.Windows.Forms.md)

# Dependency: VbLargeFileDocTest -> System.Windows.Forms

| Field | Value |
|---|---|
| type | Reference |
| project | VbLargeFileDocTest |
| target | System.Windows.Forms |
| source | VbLargeFileDocTest.vbproj |

## Maintenance Notes

- 確認版本、部署路徑、x86/x64 相容性。
- 若為 SDK / COM / Native DLL，需確認 runtime 與授權。


### [Dependency: VbLargeFileDocTest -> System.Configuration](chunks/dependencies/0001_VbLargeFileDocTest_System.Configuration.md)

# Dependency: VbLargeFileDocTest -> System.Configuration

| Field | Value |
|---|---|
| type | Reference |
| project | VbLargeFileDocTest |
| target | System.Configuration |
| source | VbLargeFileDocTest.vbproj |

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


### [External Dependency: Reference](chunks/dependencies/external_0003_Reference.md)

# External Dependency: Reference

| Field | Value |
|---|---|
| dependency_type | Reference |
| name | System.Windows.Forms |
| project | VbLargeFileDocTest |
| purpose | Referenced dependency |
| risk | Version or deployment mismatch risk |
| confidence | 0.75 |

## Maintenance Notes

- 確認版本、部署路徑、x86/x64 相容性。
- 若為 SDK / COM / Native DLL，需確認 runtime 與授權。


### [External Dependency: Reference](chunks/dependencies/external_0004_Reference.md)

# External Dependency: Reference

| Field | Value |
|---|---|
| dependency_type | Reference |
| name | System.Configuration |
| project | VbLargeFileDocTest |
| purpose | Referenced dependency |
| risk | Version or deployment mismatch risk |
| confidence | 0.75 |

## Maintenance Notes

- 確認版本、部署路徑、x86/x64 相容性。
- 若為 SDK / COM / Native DLL，需確認 runtime 與授權。

