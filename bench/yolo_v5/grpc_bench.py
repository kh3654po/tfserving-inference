#import grpc module
from module import module_grpc
from tensorflow_serving.apis import predict_pb2

#tf log setting
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

#병렬처리 library
import concurrent.futures

def run_bench(num_tasks, server_address, use_https, data):
    model_name = "yolo_v5"

    stub = module_grpc.create_grpc_stub(server_address, use_https)

    # gRPC 요청 생성
    request = predict_pb2.PredictRequest()
    request.model_spec.name = model_name
    request.model_spec.signature_name = 'serving_default'
    request.inputs['x'].CopyFrom(data)

    # gRPC 요청 병렬 처리
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_tasks) as executor:
        futures = [executor.submit(lambda: module_grpc.predict(stub, request)) for _ in range(num_tasks)]

    inference_times_include_network_latency = []
    # 결과 출력
    for future in concurrent.futures.as_completed(futures):
        result, thread_elapsed_time  = future.result()
        inference_times_include_network_latency.append(thread_elapsed_time)

    return inference_times_include_network_latency
