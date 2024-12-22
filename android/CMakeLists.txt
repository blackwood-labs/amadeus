cmake_minimum_required(VERSION 3.4.1)

add_library( amadeus SHARED src/main/cpp/amadeus.cpp )

add_library( fmod SHARED IMPORTED )
set_target_properties(
  fmod PROPERTIES
  IMPORTED_LOCATION "${SRC_ROOT}/main/libfmod/${ANDROID_ABI}/libfmod.so"
  INTERFACE_INCLUDE_DIRECTORIES "${SRC_ROOT}/main/libfmod/inc"
)
target_link_libraries( amadeus fmod )

add_library( fmod_studio SHARED IMPORTED )
set_target_properties(
  fmod_studio PROPERTIES
  IMPORTED_LOCATION "${SRC_ROOT}/main/libfmod/${ANDROID_ABI}/libfmodstudio.so"
  INTERFACE_INCLUDE_DIRECTORIES "${SRC_ROOT}/main/libfmod/inc"
)
target_link_libraries( amadeus fmod_studio )