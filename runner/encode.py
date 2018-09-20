import re


class Encoder:
    def __init__(self, proto):
        self.prototype = proto

    def _encode_type(self, type, value):
        rc = ""
        key = type["type"]

        if "items" in type.keys():
            col_type = type["items"]
            fn = self._encode_collections[key][0]
            rc = fn(self, col_type, value)
        else:
            fn = self._encode_values[key][0]
            rc = fn(self, value)
        return rc

    def _decode_type(self, type, encoded):
        rc = ""
        key = type["type"]

        if "items" in type.keys():
            col_type = type["items"]
            fn = self._encode_collections[key][1]
            rc, encoded = fn(self, col_type, encoded)
        else:
            fn = self._encode_values[key][1]
            rc, encoded = fn(self, encoded)
        return rc, encoded

    # take a tuple of args and convert it to a string
    def encode_params(self, args):
        # args map onto prototype->args
        # only positional, required args are supported
        answer = ""
        pairs = zip(self.prototype['args'], args)
        for pair in pairs:
            answer += f'{self._encode_type(pair[0], pair[1])}\n'
        return answer

    # take a string and convert it to a tuple of args
    def decode_params(self, encoded):
        answer = []
        pairs = zip(self.prototype['args'], encoded.splitlines())
        for pair in pairs:
            param = pair[0]
            line = pair[1]
            rc = self._decode_type(param, line)
            answer.append(rc[0])
        return answer

    # take a rc, tuple of args and convert it to return
    def encode_return(self, rc):
        # args map onto prototype->args
        # only positional, required args are supported
        answer = self._encode_type(self.prototype, rc)
        return answer

    # take a string and convert it to the return
    def decode_return(self, encoded):
        rc, encoded = self._decode_type(self.prototype, encoded)
        return rc, encoded

    def _encode_string(self, value):
        print("encoding " + value)
        rc = '"{}"'.format(value)
        return rc

    def _decode_string(self, encoded):
        m = re.match(r'\"(.*?)\"', encoded)
        rc = ""
        if m:
            encoded = encoded[m.span()[1]:]
            rc = m.group(1)
        return rc, encoded

    def _encode_integer(self, value):
        rc = str(value)
        return rc

    def _decode_integer(self, encoded):
        # 42,43,25
        # rc -> 42
        # encoded -> ,43,25
        for ix in range(len(encoded)):
            if not encoded[ix].isdigit():
                rc = int(encoded[0:ix])
                encoded = encoded[ix:]
                return rc, encoded
        return -1, ""

    def _encode_array(self, type, value):
        rc = "["
        for item in value:
            rc += self._encode_type(type, item) + ','
        if len(value) > 0:
            rc = rc[:-1]
        rc += "]"
        return rc;

    def _decode_array(self, type, encoded):

        answer = []

        encoded = encoded[encoded.find('[')+1:]

        while len(encoded) > 0:
            encoded = encoded.lstrip()
            if encoded[0] == ']':
                return answer, encoded[1:]
            if encoded[0] == ',':
                encoded = encoded[1:]
            rc, encoded = self._decode_type(type, encoded)
            answer.append(rc)


    _encode_collections = {
            "array": (_encode_array, _decode_array),
        }
    _encode_values = {
            "string": (_encode_string, _decode_string),
            "integer": (_encode_integer, _decode_integer)
        }


# example: def SayHello(who):
# return "hello " + who
# fn name: SayHello, return type: string, parameter: who, parameter type: string
# protos = [
#     {
#       "name": "SayHello",
#       "type": "string",
#       "args": [{"name": "who", "type": "string"}]
#     },
#     {
#       "name": "ReverseList",
#       "type": "array",
#       "items": {"type" : "integer"},
#       "args": [{"name": "nums", "type": "array", "items": {"type": "integer"}}]
#     },
#     {
#       "name": "FindPrimes",
#       "type": "array",
#       "items": {"type": "integer"},
#       "args": [{"name": "num", "type": "integer"}]
#     },
#     {
#         "name": "JoinString",
#         "type": "string",
#         "args": [{"name": "words", "type": "array", "items": {"type": "string"}}]
#     }
# ]
#
# encoder = Encoder(protos[1])
# #encoded = encoder.encode_params([[3, 4, 5, 6]])
# encoded = encoder.encode_return([3, 4, 5, 6])
# print("encoded: " + encoded)
# #params = encoder.decode_params(encoded)
# params = encoder.decode_return(encoded)
# print("decoded: " + str(params))

