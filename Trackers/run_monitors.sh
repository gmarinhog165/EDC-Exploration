#!/bin/bash

# Remover ficheiros CSV se existirem
rm -f dataflow_timing.csv edc_enhanced_timing.csv

# Obter nomes dos pods dinamicamente
DATA_PLANE_POD=$(kubectl get pods -n mvd -o name | grep provider-qna-dataplane | cut -d'/' -f2)
CONTROL_PLANE_POD=$(kubectl get pods -n mvd -o name | grep provider-qna-controlplane | cut -d'/' -f2)

# Verificações de segurança
if [[ -z "$DATA_PLANE_POD" || -z "$CONTROL_PLANE_POD" ]]; then
    echo "Erro: Não foi possível encontrar os pods necessários."
    exit 1
fi

# Executar scripts Python
python3 k8s_log_monitor.py "$DATA_PLANE_POD" -n mvd
python3 edc_control_plane_monitor.py "$CONTROL_PLANE_POD" -n mvd

