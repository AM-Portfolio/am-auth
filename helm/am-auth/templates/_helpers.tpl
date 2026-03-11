{{/*
Expand the name of the chart.
*/}}
{{- define "am-auth.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "am-auth.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
environment: {{ .Values.environment }}
{{- end }}

{{/*
Vault Agent Sidecar Injector annotations
Usage: {{- include "am-auth.vaultAnnotations" (dict "root" . "secrets" (list "jwt" "database")) }}

How it works:
  1. Vault Agent sidecar authenticates to Vault using Kubernetes ServiceAccount JWT
  2. It fetches the secret at each Vault path
  3. Writes a sourceable shell file to /vault/secrets/env
  4. Container command sources that file before starting the app
*/}}
{{- define "am-auth.vaultAnnotations" -}}
vault.hashicorp.com/agent-inject: "true"
vault.hashicorp.com/role: {{ .root.Values.global.vault.role | quote }}
vault.hashicorp.com/auth-path: {{ .root.Values.global.vault.authPath | quote }}
vault.hashicorp.com/agent-pre-populate-only: "false"
{{- range .secrets }}
{{- $path := index .root.Values.global.vault.secrets . }}
vault.hashicorp.com/agent-inject-secret-{{ . }}: {{ $path | quote }}
vault.hashicorp.com/agent-inject-template-{{ . }}: |
  {{`{{`}}- with secret {{ $path | quote }} {{`}}`}}
  {{`{{`}}- range $key, $val := .Data.data {{`}}`}}
  export {{`{{`}} $key {{`}}`}}="{{`{{`}} $val {{`}}`}}"
  {{`{{`}} end {{`}}`}}
  {{`{{`}} end {{`}}`}}
{{- end }}
vault.hashicorp.com/agent-inject-file: "env"
{{- end }}

{{/*
Vault-aware container command
Sources /vault/secrets/env before starting the app.
Usage: {{ include "am-auth.vaultCommand" (list "uvicorn" "main:app" "--host" "0.0.0.0" "--port" "8001") }}
*/}}
{{- define "am-auth.vaultCommand" -}}
command: ["/bin/sh", "-c"]
args:
  - |
    . /vault/secrets/jwt 2>/dev/null || true
    . /vault/secrets/database 2>/dev/null || true
    . /vault/secrets/redis 2>/dev/null || true
    . /vault/secrets/kafka 2>/dev/null || true
    . /vault/secrets/internal-jwt 2>/dev/null || true
    exec {{ . | join " " }}
{{- end }}
