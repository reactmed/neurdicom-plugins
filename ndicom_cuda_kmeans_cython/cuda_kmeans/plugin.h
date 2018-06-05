class Plugin {

public:

    Plugin(int *INPLACE_ARRAY1, int DIM1);

    ~Plugin();

    int* process();
    
private:
    int *array_device;
    int *array_host;
    int length;
};