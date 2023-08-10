#pragma once

#include <forstio/codec/schema.h>

namespace kel {
namespace gasp {
namespace schema {
using namespace saw::schema;

using Function = Struct<
	Member<String, "return_type">,
	Member<String, "function_name">,
	Member<Array<String>, "parameter_types">
>;

using Variable = Struct<>;

using Class = Struct<
	Member<String, "class_name">,
	Member<Array<Function>, "public_functions">,
	Member<Array<Function>, "protected_functions">,
	Member<Array<Function>, "private_functions">,
	Member<Array<String>, "parents">
>;


}
}
}
