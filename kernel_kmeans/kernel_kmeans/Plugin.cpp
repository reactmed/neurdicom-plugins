#include "Plugin.h"
#include <json.hpp>
#include <iostream>
#include <stack>
#include <cmath>
#include <random>

using json = nlohmann::json;
using namespace std;

#define PI 3.1459
#define PI_DIV_2 1.57079
#define PI_SQ_DIV_16 0.61685
#define THREE_DIV_FOUR_SQ 0.0625
#define MINUS_HALF -0.5f
#define ONE_DIV_2PI_SQ 0.02533

typedef float (*dist_func)(const float&, const float&);

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

inline float triangleDist(const float &a, const float &b){
    float a1 = 1 - a;
    float b1 = 1 - b;
    return a1 * a1 + b1 * b1 - 2 * a1 * b1;
}

inline float cosDist(const float &a, const float &b){
    float cosA = cos(a * PI_DIV_2);
    float cosB = cos(b * PI_DIV_2);
    float cosAMinusCosB = cosA - cosB;
    return PI_SQ_DIV_16 * cosAMinusCosB * cosAMinusCosB;
}

inline float epanechnikovDist(const float &a, const float &b){
    float c = (a * a - b * b);
    return 0.0625 * c * c;
}

inline float gaussDist(const float &a, const float &b){
    float aSq = a * a;
    float bSq = b * b;
    float expA = exp(-aSq);
    float expB = exp(-bSq);
    return ONE_DIV_2PI_SQ * (expA + expB - 2 * exp(MINUS_HALF * (aSq + bSq)));
}

const dist_func cosDist_Ptr = cosDist;
const dist_func triangleDist_Ptr = triangleDist; 
const dist_func epanechnikovDist_Ptr = epanechnikovDist;
const dist_func gaussDist_Ptr = gaussDist;

inline void relabel(const float *img, const float* clusters, int n, int nClusters, int* labels, dist_func distFunc){
    for(int i = 0; i < n; i++){
        float minDist = 100.0f;
        int label = 0;
        for(int j = 0; j < nClusters; j++){
            float dist = distFunc(img[i], clusters[j]);
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

inline float calcObj(const float* img, const int* labels, const float* clusters, int n, int nClusters, dist_func distFunc){
    float obj = 0.0f;
    for(int i = 0; i < n; i++){
        for(int j = 0; j < nClusters; j++){
            float dist = distFunc(clusters[j], img[i]);
            obj += dist;
        }
    }
    return obj;
}

inline int *processInstance(const float *img, int w, int h, int nClusters, int maxIt, float eps, string kernel) {
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
    dist_func distFunc;
    if(kernel == "cos"){
        distFunc = cosDist_Ptr;
    }
    else if(kernel == "triangular"){
        distFunc = triangleDist_Ptr;
    }
    else if(kernel == "gauss"){
        distFunc = gaussDist_Ptr;
    }
    else{
        distFunc = epanechnikovDist_Ptr;
    }
    while(++it <= maxIt){
        relabel(img, clusters, n, nClusters, labels, distFunc);
        calcNewCenters(img, labels, n, nClusters, clusters);
        obj1 = calcObj(img, labels, clusters, n, nClusters, distFunc);
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
    float eps;
    SET_OR_DEFAULT(kernel, paramsMap, "kernel", "cos", string);
    SET_OR_DEFAULT(nClusters, paramsMap, "n_clusters", 2, int);
    SET_OR_DEFAULT(maxIt, paramsMap, "max_it", 100, int);
    SET_OR_DEFAULT(eps, paramsMap, "eps", 0.001f, float);
    auto *res = processInstance(img, w, h, nClusters, maxIt, eps, kernel);
    return res;
}

Plugin::Plugin() {

    cout << "Initializing plugin" << endl;
}

Plugin::~Plugin() {
    cout << "Destroying plugin" << endl;
}
