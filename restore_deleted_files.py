import subprocess
import re
import os

def restore_files(commit_file):
    """
    Analisa o arquivo de commits e restaura os arquivos deletados.
    """
    print(f"Iniciando a restauração de arquivos deletados a partir de {commit_file}...")
    
    # Lista para armazenar os arquivos restaurados
    restored_files = []
    
    # Padrão para identificar o commit hash
    commit_pattern = re.compile(r'^[0-9a-f]{40}$')
    
    # Padrão para identificar o arquivo deletado (D\t<caminho_do_arquivo>)
    # O re.escape é usado para tratar nomes de arquivos com caracteres especiais (como aspas)
    file_pattern = re.compile(r'^D\t(.+)$')
    
    current_commit = None
    
    with open(commit_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if commit_pattern.match(line):
                current_commit = line
            elif current_commit and file_pattern.match(line):
                # Extrai o nome do arquivo
                match = file_pattern.match(line)
                file_path_raw = match.group(1)
                
                # Remove as aspas se existirem (para arquivos com caracteres especiais)
                file_path = file_path_raw.strip('"')
                
                # O commit que deletou o arquivo é o current_commit.
                # Queremos o estado do arquivo ANTES da exclusão, que é o commit pai (current_commit^).
                
                # Verifica se o arquivo já existe no diretório de trabalho (pode ter sido restaurado em um commit anterior)
                if os.path.exists(file_path):
                    print(f"Arquivo '{file_path}' já existe no diretório de trabalho. Pulando.")
                    continue

                # Comando git checkout para restaurar o arquivo
                # Usamos --force para garantir que o arquivo seja sobrescrito se houver conflito
                command = f'git checkout {current_commit}^ -- "{file_path}"'
                
                print(f"Restaurando '{file_path}' do commit {current_commit}^...")
                
                try:
                    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                    if result.stderr:
                        print(f"Erro ao restaurar '{file_path}': {result.stderr.strip()}")
                    else:
                        print(f"Sucesso ao restaurar '{file_path}'.")
                        restored_files.append(file_path)
                except subprocess.CalledProcessError as e:
                    print(f"Falha ao executar comando para '{file_path}': {e.stderr.strip()}")
                    
    print("\n--- Resumo da Restauração ---")
    if restored_files:
        print(f"Total de arquivos restaurados: {len(restored_files)}")
        print("Arquivos restaurados:")
        for f in restored_files:
            print(f"- {f}")
    else:
        print("Nenhum arquivo foi restaurado.")
        
    # Salva a lista de arquivos restaurados em um arquivo para o próximo passo
    with open('restored_files_list.txt', 'w', encoding='utf-8') as f:
        for file in restored_files:
            f.write(file + '\n')

if __name__ == "__main__":
    # O arquivo de commits está no diretório pai
    os.chdir('produtos-nutricionais')
    restore_files('../deleted_files_with_commits.txt')
    
