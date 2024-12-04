import os
import xml.etree.ElementTree as ET
import requests
from graphviz import Digraph
import networkx as nx
import datetime

# Загрузка конфигурации
def load_config(config_file):
    tree = ET.parse(config_file)
    root = tree.getroot()
    
    config = {
        "graphviz_path": root.find("graphviz_path").text,
        "package_name": root.find("package_name").text,
        "max_depth": int(root.find("max_depth").text)-1,
        "output": {
            "file_name": root.find("output/file_name").text,
            "format": root.find("output/format").text
        }
    }
    return config

# Получение зависимостей только для последней версии
def get_dependencies(package_name, max_depth):
    dependencies = {}
    visited = set()

    def fetch_dependencies(pkg, depth):
        if depth > max_depth or pkg in visited:
            return
        print(f"{datetime.datetime.now()} | Checking Dependency of {pkg}. Depth is {depth}")
        visited.add(pkg)
        url = f"https://registry.npmjs.org/{pkg}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("dist-tags", {}).get("latest") 
            if latest_version:
                version_data = data["versions"].get(latest_version, {})
                deps = version_data.get("dependencies", {})
                if deps:
                    dependencies[pkg] = list(deps.keys())
                for dep in deps:
                    fetch_dependencies(dep, depth + 1)
        else:
            print(f"Failed to fetch data for package: {pkg} (Status code: {response.status_code})")
    
    fetch_dependencies(package_name, 0)
    return dependencies

# Создание графа зависимостей
def create_dependency_graph(dependencies):
    graph = nx.DiGraph()
    for pkg, deps in dependencies.items():
        graph.add_node(pkg)
        for dep in deps:
            graph.add_edge(pkg, dep)
    return graph

# Визуализация графа
def visualize_graph(graph, output_config):
    if not graph.nodes:
        print("No nodes in the graph to visualize!")
        return

    dot = Digraph(format=output_config['format'], engine='dot')
    for node in graph.nodes:
        dot.node(node)
    for edge in graph.edges:
        dot.edge(edge[0], edge[1])

    # Сохранение Graphviz кода в .dot файл
    dot_file_path = os.path.join(os.getcwd(), f"{output_config['file_name']}.dot")
    with open(dot_file_path, 'w') as dot_file:
        dot_file.write(dot.source)
    print(f"Graphviz code saved to {dot_file_path}")
    
    # Генерация PNG и сохранение в файл
    output_path = os.path.join(os.getcwd(), f"{output_config['file_name']}")
    dot.render(output_path, cleanup=True)
    print(f"Graph visualized and saved as {output_path}")

# Основной скрипт
def main(config_file):
    config = load_config(config_file)
    print("Configuration loaded:", config)
    
    dependencies = get_dependencies(config["package_name"], config["max_depth"])
    print(f"Dependencies fetched: {dependencies}")
    
    graph = create_dependency_graph(dependencies)
    print(f"Graph nodes: {list(graph.nodes)}")
    print(f"Graph edges: {list(graph.edges)}")
    
    visualize_graph(graph, config["output"])

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python visualize_dependencies.py <config_file>")
    else:
        main(sys.argv[1])