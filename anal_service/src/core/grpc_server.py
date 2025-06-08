import grpc
from concurrent import futures

from proto import dashboard_anal_pb2_grpc
from src.core.analysis_service_impl import AnalysisServiceImpl


def serve_grpc_server():
    # Создаём сервер с пулом из 10 потоков
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Регистрируем реализацию сервиса на сервере
    dashboard_anal_pb2_grpc.add_AnalysisServiceServicer_to_server(
        AnalysisServiceImpl(), server
    )

    # Добавляем небезопасный (без TLS) порт для прослушивания
    server.add_insecure_port("localhost:50051")
    print("[gRPC] Server started at localhost:50051")

    # Запускаем сервер (в отдельном потоке)
    server.start()
    # Ждём завершения работы сервера (например, по Ctrl+C)
    server.wait_for_termination()


if __name__ == "__main__":
    serve_grpc_server()
