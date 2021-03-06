#!/usr/bin/env python3
from concurrent import futures
import grpc
import os
import time

from skillitor.core.api import skillitor_pb2, skillitor_pb2_grpc
from skillitor.core.command_interpreter import CommandInterpreter


class SkillitorQueryHandler(skillitor_pb2_grpc.SkillitorQueryServicer):
    def __init__(self):
        self.db_service_config = {
            'hostname': os.getenv('DB_SERVICE_HOSTNAME',
                                  'skillitor_pgsql'),
            'port': os.getenv('DB_SERVICE_PORT', 50051)
        }
        channel = grpc.insecure_channel('{hostname}:{port}'.format(
            **self.db_service_config))
        self.db_service = skillitor_pb2_grpc.SkillitorQueryStub(channel)
        self.qp = CommandInterpreter()

    def SetSkills(self, request, context):
        print("Received a call to SetSkills: " + str(request))
        return self.db_service.SetSkills(request)

    def UnsetSkills(self, request, context):
        print("Received a call to UnsetSkills: " + str(request))
        return self.db_service.UnsetSkills(request)

    def FindSkills(self, request, context):
        print("Received a call to FindSkills: " + str(request))
        return self.db_service.FindSkills(request)

    def RawCommand(self, request, context):
        print("Received a call to RawCommand: " + str(request))
        command, args = request.command_text.split(' ', 2)
        response = "Real response will go here."
        if command == 'skillset':
            self.qp.process_set_cmd('web-user@example.com', self.db_service,
                                    args)
        elif command == 'skillunset':
            self.qp.process_set_cmd('web-user@example.com', self.db_service,
                                    args, unset=True)
        elif command == 'skillfind':
            self.qp.process_find_cmd(self.db_service, args)
        else:
            response = (
                "Usage:\n"
                "skillset|skillunset <skill_list> [for <email>]\n"
                "skillfind any|all <skill_list>\n")

        return skillitor_pb2.RawResponse(text=response)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    skillitor_pb2_grpc.add_SkillitorQueryServicer_to_server(
        SkillitorQueryHandler(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Listening on port 50051")

    # The server code above runs asynchronously, so we need to do a sleep loop
    # to avoid exiting.
    while True:
        time.sleep(10)
        # Time passes. If only we had something useful to do.


if __name__ == '__main__':
    serve()
