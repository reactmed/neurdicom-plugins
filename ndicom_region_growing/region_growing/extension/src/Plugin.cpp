#include "Plugin.h"
#include <json.hpp>
#include <iostream>
#include <stack>
#include <cmath>

using json = nlohmann::json;
using namespace std;

struct Pos {
    int x, y;

    Pos(int x, int y) {
        this->x = x;
        this->y = y;
    }
};

#define SET_OR_DEFAULT(VAR, JSON, NAME, DEFAULT, TYPE)\
    if((JSON)[NAME].is_null()){\
        (VAR) = (DEFAULT);\
    }\
    else{\
        (VAR) = (JSON)[NAME].get<TYPE>();\
    }

#define CLAMP(VAL, BOUND_MIN, BOUND_MAX)\
    (VAL) > (BOUND_MAX) ? (BOUND_MAX) : ((VAL) < (BOUND_MIN) ? (BOUND_MIN) : (VAL))

#define POS_OFFSET(POS, X_OFFSET, Y_OFFSET, W, H)\
    Pos(CLAMP((POS).x + (X_OFFSET), 0, (W) - 1), CLAMP((POS).y + (Y_OFFSET), 0, (H) - 1))

// inline int *processInstance(const float *img, int w, int h, int index, Pos seed, float th) {
//     auto *res = new int[w * h];
//     memset(res, 0, sizeof(int) * w * h);
//     stack<Pos> bag;
//     bag.push(seed);
//     while (!bag.empty()) {
//         Pos current = bag.top();
//         bag.pop();
//         for (int xOff = -1; xOff <= 1; xOff++) {
//             for (int yOff = -1; yOff <= 1; yOff++) {
//                 Pos neighbor = POS_OFFSET(current, xOff, yOff, w, h);
//                 if (!res[neighbor.x + neighbor.y * w]) {
//                     float dist = fabs(img[neighbor.x + neighbor.y * w + index] - img[seed.x + seed.y * w + index]);
//                     if (dist <= th) {
//                         res[neighbor.x + neighbor.y * w] = 1;
//                         bag.push(neighbor);
//                     }
//                 }
//             }
//         }
//     }
//     return res;
// }

inline int *processInstance(const float *img, int w, int h, Pos seed, float th) {
    auto *res = new int[w * h];
    memset(res, 0, sizeof(int) * w * h);
    stack<Pos> bag;
    bag.push(seed);
    while (!bag.empty()) {
        Pos current = bag.top();
        bag.pop();
        for (int xOff = -1; xOff <= 1; xOff++) {
            for (int yOff = -1; yOff <= 1; yOff++) {
                Pos neighbor = POS_OFFSET(current, xOff, yOff, w, h);
                if (!res[neighbor.x + neighbor.y * w]) {
                    float seedIntensity = img[seed.x + seed.y * w];
                    float neighborIntensity = img[neighbor.x + neighbor.y * w];
                    float dist = fabs(seedIntensity - neighborIntensity);
                    if (dist <= th) {
                        res[neighbor.x + neighbor.y * w] = 1;
                        bag.push(neighbor);
                    }
                }
            }
        }
    }
    return res;
}

// int *Plugin::process(const float *img, const int *imagesSizes, int imagesCount, const char *params) {
//     cout << "Processing image" << endl;
//     cout << params << endl;
//     auto paramsMap = json::parse(params);
//     int x, y, th;
//     SET_OR_DEFAULT(th, paramsMap, "threshold", 1.0f, float);
//     SET_OR_DEFAULT(x, paramsMap, "seedPointX", 0, int);
//     SET_OR_DEFAULT(y, paramsMap, "seedPointY", 0, int);
//     Pos seed(x, y);
//     int totalSize = 0;
//     for (int i = 0; i < imagesCount; i++) {
//         totalSize += imagesSizes[i] * imagesSizes[i + 1];
//     }
//     auto *res = new int[totalSize];
//     int index = 0;
//     for (int i = 0; i < imagesCount; i++) {
//         int w = imagesSizes[i];
//         int h = imagesSizes[i + 1];
//         const int *partialRes = processInstance(img, w, h, index, seed, th);
//         memcpy(&res[index], partialRes, sizeof(int) * w * h);
//         index += w * h;
//     }
//     return res;
// }

int *Plugin::process(const float *img, const int w, const int h, const char *params) {
    cout << "Processing image" << endl;
    cout << params << endl;
    auto paramsMap = json::parse(params);
    int x, y;
    float th;
    SET_OR_DEFAULT(th, paramsMap, "threshold", 1.0f, float);
    SET_OR_DEFAULT(x, paramsMap, "seedPointX", 0, int);
    SET_OR_DEFAULT(y, paramsMap, "seedPointY", 0, int);
    Pos seed(x, y);
    cout << "threshold: " << th << endl;
    auto *res = processInstance(img, w, h, seed, th);
    return res;
}

Plugin::Plugin() {
    cout << "Initializing plugin" << endl;
}

Plugin::~Plugin() {
    cout << "Destroying plugin" << endl;
}
