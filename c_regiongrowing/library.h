#ifndef C_REGIONGROWING_LIBRARY_H
#define C_REGIONGROWING_LIBRARY_H

#include "Plugin.h"

extern "C" Plugin* InitPlugin();
extern "C" int * Process(Plugin *plugin, const float *img, int width, int height, const char *params);
extern "C" void DestroyPlugin(Plugin* plugin);

#endif