# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: echo/proto/echo/v1/echo.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    0,
    '',
    'echo/proto/echo/v1/echo.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1d\x65\x63ho/proto/echo/v1/echo.proto\x12\x07\x65\x63ho.v1\"#\n\x10\x44\x65moUnaryRequest\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\"$\n\x11\x44\x65moUnaryResponse\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\"-\n\x1a\x44\x65moServerStreamingRequest\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\".\n\x1b\x44\x65moServerStreamingResponse\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\"-\n\x1a\x44\x65moClientStreamingRequest\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\".\n\x1b\x44\x65moClientStreamingResponse\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\"4\n!DemoBidirectionalStreamingRequest\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\"5\n\"DemoBidirectionalStreamingResponse\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t2\x94\x03\n\x0b\x45\x63hoService\x12\x42\n\tDemoUnary\x12\x19.echo.v1.DemoUnaryRequest\x1a\x1a.echo.v1.DemoUnaryResponse\x12\x62\n\x13\x44\x65moServerStreaming\x12#.echo.v1.DemoServerStreamingRequest\x1a$.echo.v1.DemoServerStreamingResponse0\x01\x12\x62\n\x13\x44\x65moClientStreaming\x12#.echo.v1.DemoClientStreamingRequest\x1a$.echo.v1.DemoClientStreamingResponse(\x01\x12y\n\x1a\x44\x65moBidirectionalStreaming\x12*.echo.v1.DemoBidirectionalStreamingRequest\x1a+.echo.v1.DemoBidirectionalStreamingResponse(\x01\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'echo.proto.echo.v1.echo_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_DEMOUNARYREQUEST']._serialized_start=42
  _globals['_DEMOUNARYREQUEST']._serialized_end=77
  _globals['_DEMOUNARYRESPONSE']._serialized_start=79
  _globals['_DEMOUNARYRESPONSE']._serialized_end=115
  _globals['_DEMOSERVERSTREAMINGREQUEST']._serialized_start=117
  _globals['_DEMOSERVERSTREAMINGREQUEST']._serialized_end=162
  _globals['_DEMOSERVERSTREAMINGRESPONSE']._serialized_start=164
  _globals['_DEMOSERVERSTREAMINGRESPONSE']._serialized_end=210
  _globals['_DEMOCLIENTSTREAMINGREQUEST']._serialized_start=212
  _globals['_DEMOCLIENTSTREAMINGREQUEST']._serialized_end=257
  _globals['_DEMOCLIENTSTREAMINGRESPONSE']._serialized_start=259
  _globals['_DEMOCLIENTSTREAMINGRESPONSE']._serialized_end=305
  _globals['_DEMOBIDIRECTIONALSTREAMINGREQUEST']._serialized_start=307
  _globals['_DEMOBIDIRECTIONALSTREAMINGREQUEST']._serialized_end=359
  _globals['_DEMOBIDIRECTIONALSTREAMINGRESPONSE']._serialized_start=361
  _globals['_DEMOBIDIRECTIONALSTREAMINGRESPONSE']._serialized_end=414
  _globals['_ECHOSERVICE']._serialized_start=417
  _globals['_ECHOSERVICE']._serialized_end=821
# @@protoc_insertion_point(module_scope)
