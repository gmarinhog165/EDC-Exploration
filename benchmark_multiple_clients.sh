#!/bin/bash

# Script para inicializar múltiplos clientes com servidores Python e Java
# Uso: ./script.sh <numero_de_clientes>

# Verifica se foi fornecido o número de clientes
if [ $# -eq 0 ]; then
    echo "Erro: É necessário fornecer o número de clientes como argumento"
    echo "Uso: $0 <numero_de_clientes>"
    exit 1
fi

NUM_CLIENTES=$1

# Verifica se o argumento é um número válido
if ! [[ "$NUM_CLIENTES" =~ ^[0-9]+$ ]] || [ "$NUM_CLIENTES" -le 0 ]; then
    echo "Erro: O número de clientes deve ser um número inteiro positivo"
    exit 1
fi

echo "Inicializando $NUM_CLIENTES cliente(s)..."

# Array para armazenar os PIDs dos processos
PIDS_PYTHON=()
PIDS_JAVA=()

# Função para limpar processos em caso de interrupção
cleanup() {
    echo
    echo "Interrompendo todos os processos..."
    
    # Mata os processos Python
    for pid in "${PIDS_PYTHON[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "Parando servidor Python (PID: $pid)"
            kill -TERM "$pid" 2>/dev/null
        fi
    done
    
    # Mata os processos Java
    for pid in "${PIDS_JAVA[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "Parando servidor Java (PID: $pid)"
            kill -TERM "$pid" 2>/dev/null
        fi
    done
    
    # Aguarda um pouco e força a terminação se necessário
    sleep 2
    for pid in "${PIDS_PYTHON[@]}" "${PIDS_JAVA[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill -KILL "$pid" 2>/dev/null
        fi
    done
    
    exit 0
}

# Configura trap para capturar Ctrl+C
trap cleanup SIGINT SIGTERM

# Diretório base (absoluto)
BASE_DIR=$(pwd)

# Porta inicial
PORTA_BASE=3000

# Loop para inicializar cada cliente
for ((i=1; i<=NUM_CLIENTES; i++)); do
    # Calcula a porta para este cliente (incrementa de 10 em 10 para dar espaço)
    PORTA=$((PORTA_BASE + (i-1) * 10))
    
    echo "--- Cliente $i ---"
    echo "Porta base: $PORTA"
    echo "Portas utilizadas: $PORTA e $((PORTA + 1))"
    
    # Verifica se as portas estão disponíveis
    if netstat -tuln 2>/dev/null | grep -q ":$PORTA "; then
        echo "Aviso: Porta $PORTA já está em uso!"
    fi
    
    if netstat -tuln 2>/dev/null | grep -q ":$((PORTA + 1)) "; then
        echo "Aviso: Porta $((PORTA + 1)) já está em uso!"
    fi
    
    # Inicializa servidor Python (executa a partir do diretório correto)
    echo "Iniciando servidor Python na porta $PORTA..."
    cd ClienteProgramatico/
    python3 -u edcPythonServer.py $PORTA > "${BASE_DIR}/python_cliente_${i}.log" 2>&1 &
    PID_PYTHON=$!
    PIDS_PYTHON+=($PID_PYTHON)
    cd "$BASE_DIR"
    echo "Servidor Python iniciado (PID: $PID_PYTHON)"
    
    # Aguarda um pouco para o servidor Python inicializar
    sleep 2
    
    # Inicializa servidor Java
    echo "Iniciando servidor Java na porta $PORTA..."
    cd JavaEDCliente/
    timestamp=$(date +"%Y-%m-%d_%H-%M-%S.%3N")
mvn exec:java -Dexec.mainClass="pt.uminho.di.Benchmark.Main" -Dexec.args="$PORTA" > "${BASE_DIR}/java_cliente_${i}_${timestamp}.log" 2>&1 &
    PID_JAVA=$!
    PIDS_JAVA+=($PID_JAVA)
    cd "$BASE_DIR"
    echo "Servidor Java iniciado (PID: $PID_JAVA)"
    
    echo "Cliente $i inicializado com sucesso!"
    echo
    
    # Aguarda 2 segundos antes de inicializar o próximo cliente
    if [ $i -lt $NUM_CLIENTES ]; then
        echo "Aguardando 2 segundos antes do próximo cliente..."
        sleep 2
        echo
    fi
done

echo "Todos os $NUM_CLIENTES cliente(s) foram inicializados!"
echo
echo "Resumo dos processos:"
for ((i=1; i<=NUM_CLIENTES; i++)); do
    PORTA=$((PORTA_BASE + (i-1) * 10))
    echo "Cliente $i - Porta $PORTA:"
    echo "  Python PID: ${PIDS_PYTHON[$((i-1))]}"
    echo "  Java PID: ${PIDS_JAVA[$((i-1))]}"
done

echo
echo "Logs disponíveis:"
echo "  python_cliente_N.log - logs dos servidores Python"
echo "  java_cliente_N.log - logs dos servidores Java"
echo
echo "Pressione Ctrl+C para parar todos os processos..."

# Mantém o script rodando e monitora os processos
while true; do
    sleep 5
    
    # Verifica se algum processo morreu
    for ((i=1; i<=NUM_CLIENTES; i++)); do
        PID_PYTHON=${PIDS_PYTHON[$((i-1))]}
        PID_JAVA=${PIDS_JAVA[$((i-1))]}
        
        if ! kill -0 "$PID_PYTHON" 2>/dev/null; then
            echo "Aviso: Servidor Python do cliente $i (PID: $PID_PYTHON) parou!"
        fi
        
        if ! kill -0 "$PID_JAVA" 2>/dev/null; then
            echo "Aviso: Servidor Java do cliente $i (PID: $PID_JAVA) parou!"
        fi
    done
done
