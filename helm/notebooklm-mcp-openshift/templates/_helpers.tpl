{{/*
Expand the name of the chart.
*/}}
{{- define "notebooklm-mcp-openshift.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "notebooklm-mcp-openshift.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "notebooklm-mcp-openshift.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "notebooklm-mcp-openshift.labels" -}}
helm.sh/chart: {{ include "notebooklm-mcp-openshift.chart" . }}
{{ include "notebooklm-mcp-openshift.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: notebooklm-mcp
app.openshift.io/runtime: python
app.openshift.io/runtime-version: "3.12"
{{- end }}

{{/*
Selector labels
*/}}
{{- define "notebooklm-mcp-openshift.selectorLabels" -}}
app.kubernetes.io/name: {{ include "notebooklm-mcp-openshift.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "notebooklm-mcp-openshift.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "notebooklm-mcp-openshift.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate image pull policy
*/}}
{{- define "notebooklm-mcp-openshift.imagePullPolicy" -}}
{{- .Values.image.pullPolicy | default "IfNotPresent" }}
{{- end }}

{{/*
Generate full image name
*/}}
{{- define "notebooklm-mcp-openshift.image" -}}
{{- if .Values.imageStream.enabled }}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- end }}
{{- end }}

{{/*
Return the proper SCC name
*/}}
{{- define "notebooklm-mcp-openshift.sccName" -}}
{{- if .Values.securityContext.createCustomSCC }}
{{- include "notebooklm-mcp-openshift.fullname" . }}-scc
{{- else }}
{{- .Values.securityContext.sccName | default "restricted-v2" }}
{{- end }}
{{- end }}

{{/*
OpenShift route hostname
*/}}
{{- define "notebooklm-mcp-openshift.routeHost" -}}
{{- if .Values.route.host }}
{{- .Values.route.host }}
{{- else }}
{{- printf "%s-%s.apps.%s" (include "notebooklm-mcp-openshift.fullname" .) .Release.Namespace "cluster.local" }}
{{- end }}
{{- end }}

{{/*
Return the storage class name
*/}}
{{- define "notebooklm-mcp-openshift.storageClass" -}}
{{- if .Values.persistence.storageClass }}
{{- .Values.persistence.storageClass }}
{{- else }}
{{- "gp3-csi" }}
{{- end }}
{{- end }}

{{/*
OpenShift Console link URL
*/}}
{{- define "notebooklm-mcp-openshift.consoleLink.url" -}}
{{- if .Values.route.enabled }}
{{- if .Values.route.tls.enabled }}
{{- printf "https://%s" (include "notebooklm-mcp-openshift.routeHost" .) }}
{{- else }}
{{- printf "http://%s" (include "notebooklm-mcp-openshift.routeHost" .) }}
{{- end }}
{{- end }}
{{- end }}
