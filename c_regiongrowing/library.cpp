#include "library.h"

extern "C" {

    Plugin* InitPlugin(){
        return new Plugin;
    }

    int * Process(Plugin *plugin, const float *img, int width, int height, const char *params) {
        return plugin->process(img, width, height, params);
    }

    void DestroyPlugin(Plugin *plugin){
        delete plugin;
    }
}