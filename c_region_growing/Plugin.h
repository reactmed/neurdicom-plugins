//
// Created by Max Heartfield on 01.05.18.
//

#ifndef C_REGIONGROWING_PLUGIN_H
#define C_REGIONGROWING_PLUGIN_H


class Plugin {
public:
    Plugin();

    int *process(const float *img, const int *imagesSizes, int imagesCount, const char *params);

    ~Plugin();
};


#endif //C_REGIONGROWING_PLUGIN_H
