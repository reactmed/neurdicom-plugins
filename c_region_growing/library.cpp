#include "library.h"

extern "C" {

    Plugin* InitPlugin(){
        return new Plugin;
    }

    int* Process(Plugin *plugin, const float *img, const int* imagesSize, int imagesCount, const char *params) {
        return plugin->process(img, imagesSize, imagesCount, params);
    }

    void DestroyPlugin(Plugin *plugin){
        delete plugin;
    }
}