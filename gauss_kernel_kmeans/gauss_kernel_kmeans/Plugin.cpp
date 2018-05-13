#include "Plugin.h"
#include <json.hpp>
#include <iostream>
#include <stack>
#include <cmath>
#include <random>

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

inline float gaussDist(const float &a, const float &b, const float &sigma){
    float sigmaSq = 2 * sigma * sigma;
    float expA = exp(-(a * a) / sigmaSq);
    float expB = exp(-(b * b) / sigmaSq);
    return (expA - expB) * (expA - expB);
}

inline void relabel(const float *img, const float* clusters, int n, int nClusters, int* labels, float sigma){
    for(int i = 0; i < n; i++){
        float minDist = 100.0f;
        int label = 0;
        for(int j = 0; j < nClusters; j++){
            float dist = gaussDist(img[i], clusters[j], sigma);
            if(dist <= minDist){
                minDist = dist;
                label = j;
            }
        }
        labels[i] = label;
    }
}

inline void calcNewCenters(const float *img, const int* labels, int n, int nClusters, float* clusters){
    for(int k = 0; k < nClusters; k++){
        float sum = 0.0f;
        int count = 0;
        for(int i = 0; i < n; i++){
            if(labels[i] == k){
                sum += img[i];
                count++;
            }
        }
        clusters[k] = count > 0 ? sum / count : 0.0f;
    }
}

inline float calcObj(const float* img, const int* labels, const float* clusters, int n, int nClusters, float sigma){
    float obj = 0.0f;
    for(int i = 0; i < n; i++){
        for(int j = 0; j < nClusters; j++){
            float dist = gaussDist(clusters[j], img[i], sigma);
            obj += dist;
        }
    }
    return obj;
}

inline int *processInstance(const float *img, int w, int h, int nClusters, int maxIt, float eps, float sigma) {
    int *labels = new int[w * h];
    float* clusters = new float[nClusters];
    float obj0 = 0.0f;
    float obj1 = 0.0f;
    int n = w * h;
    int it = 0;
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<float> dis(0.0, 1.0);
    for(int i = 0; i < nClusters; i++)
        clusters[i] = dis(gen);
    while(++it <= maxIt){
        relabel(img, clusters, n, nClusters, labels, sigma);
        calcNewCenters(img, labels, n, nClusters, clusters);
        obj1 = calcObj(img, labels, clusters, n, nClusters, sigma);
        if(fabsf(obj1 - obj0) <= eps){
            break;
        }
        obj0 = obj1;
    }
    cout << "Iterations = " << it << endl;
    return labels;
}


int *Plugin::process(const float *img, const int w, const int h, const char *params) {
    cout << "Processing image" << endl;
    cout << params << endl;
    auto paramsMap = json::parse(params);
    string kernel;
    int nClusters, maxIt;
    float eps, sigma;
    SET_OR_DEFAULT(nClusters, paramsMap, "n_clusters", 2, int);
    SET_OR_DEFAULT(maxIt, paramsMap, "max_it", 100, int);
    SET_OR_DEFAULT(eps, paramsMap, "eps", 0.001f, float);
    SET_OR_DEFAULT(sigma, paramsMap, "sigma", 0.5f, float);
    auto *res = processInstance(img, w, h, nClusters, maxIt, eps, sigma);
    return res;
}

Plugin::Plugin() {

    cout << "Initializing plugin" << endl;
}

Plugin::~Plugin() {
    cout << "Destroying plugin" << endl;
}
