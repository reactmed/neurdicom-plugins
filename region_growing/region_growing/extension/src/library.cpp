#include "library.h"

extern "C" {

    Plugin* InitPlugin(){
        return new Plugin;
    }

    int* Process(Plugin *plugin, const float *img, const int w, const int h, const char *params) {
        return plugin->process(img, w, h, params);
    }

    void DestroyPlugin(Plugin *plugin){
        delete plugin;
    }
}