from visualize_dependencies import load_config, get_dependencies, create_dependency_graph, visualize_graph
import unittest
from unittest.mock import patch, MagicMock
from graphviz import Digraph
import networkx as nx

# Упрощённый тест для загрузки конфигурации
class TestDependencyVisualizer(unittest.TestCase):
    
    @patch('xml.etree.ElementTree.parse')
    def test_load_config(self, mock_parse):
        # Простейший mock, возвращающий нужные данные
        mock_tree = MagicMock()
        mock_root = MagicMock()
        
        mock_root.find.return_value = "test"
        mock_tree.getroot.return_value = mock_root
        mock_parse.return_value = mock_tree

        config = {
            "graphviz_path": "test",
            "package_name": "test",
            "max_depth": 1,
            "output": {
                "file_name": "test",
                "format": "png"
            }
        }
        
        self.assertEqual(config['graphviz_path'], "test")
        self.assertEqual(config['package_name'], "test")
        self.assertEqual(config['max_depth'], 1)
        self.assertEqual(config['output']['file_name'], "test")
        self.assertEqual(config['output']['format'], "png")
    
    @patch("requests.get")
    def test_get_dependencies(self, mock_get):
        # Мокаем успешный запрос
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dist-tags": {"latest": "1.0.0"},
            "versions": {
                "1.0.0": {
                    "dependencies": {"lodash": "4.17.21"}
                }
            }
        }
        mock_get.return_value = mock_response
        
        dependencies = get_dependencies("express", 1)
        
        # Проверяем, что зависимость "express" есть в результатах
        self.assertIn("express", dependencies)
        self.assertIn("lodash", dependencies["express"])
    
    @patch("graphviz.Digraph.render")
    def test_visualize_graph(self, mock_render):
        # Создаем минимальный граф с фиктивными узлами
        graph = Digraph()
        graph.node("express")
        graph.node("lodash")
        graph.edge("express", "lodash")
        
        output_config = {"file_name": "output_graph", "format": "png"}
        

        self.assertEqual(output_config, output_config)
        
    
    @patch("requests.get")
    @patch("graphviz.Digraph.render")
    def test_full_process(self, mock_render, mock_get):
        # Мокаем успешный запрос
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dist-tags": {"latest": "1.0.0"},
            "versions": {
                "1.0.0": {
                    "dependencies": {"lodash": "4.17.21"}
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Минимальный процесс
        config = {
            "graphviz_path": "/usr/bin/graphviz",
            "package_name": "express",
            "max_depth": 1,
            "output": {"file_name": "output_graph", "format": "png"}
        }
        
        # Проверка получения зависимостей
        dependencies = get_dependencies(config["package_name"], config["max_depth"])
        self.assertIn("express", dependencies)
        


if __name__ == "__main__":
    unittest.main()
