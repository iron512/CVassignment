#include <iostream>
#include <cstring>
#include <cstdlib>

#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>

using namespace std;
using namespace cv;

int main(int argc, char const *argv[]) {
    int debug = 0;
    
    Mat background;
    Mat frame, gray;
    Mat D1, b1, motion_mask;
    VideoCapture cap;

    VideoWriter outputVideo;

    if (argc != 4){
        cout << "\nError found:" << "Incorrect arguments." << "\nTerminating.\n\nRun using this command:\n\n\t" << "./track <video> <background> <debug>\n\n";
        return -1;
    }

    cap.open(argv[1]);
    background = imread(argv[2],IMREAD_GRAYSCALE);
    debug = atoi(argv[3]);

    Size S = Size((int) cap.get(CAP_PROP_FRAME_WIDTH),(int) cap.get(CAP_PROP_FRAME_HEIGHT));
    outputVideo.open("../output/ball_possession.mp4", static_cast<int>(cap.get(CAP_PROP_FOURCC)), cap.get(CAP_PROP_FPS), S, true);

    cap >> frame;
    outputVideo << frame;

    int width = frame.size().width;
    int height = frame.size().height;

    Rect2i whiteRegion(0,0,width/2,height);
    Rect2i blackRegion(width/2,0,width/2,height);

    if (!cap.isOpened()) 
        return 1;

    namedWindow("basket", 1);
    namedWindow("threshold", 1);

    int count = 0;

    int wx = whiteRegion.x;
    int wy = whiteRegion.y;

    int bx = blackRegion.x;
    int by = blackRegion.y;

    for (;;count++) {
        cap >> frame;

        if (frame.empty())
            break;

        cvtColor(frame, gray, COLOR_RGB2GRAY);

        int whiteSum = 0;
        int blackSum = 0;

        absdiff(gray, background, D1);
        threshold(D1, b1, 50, 255, THRESH_BINARY);
        motion_mask = b1;

        imshow("threshold",motion_mask);

        for (int i = 0; i < whiteRegion.width; ++i) {
            for (int j = 0; j < whiteRegion.height; ++j) {
                //cout << "ok " << i <<  " " << j << endl;
                if ((int)(motion_mask.at<uchar>(wy+j,wx+i)) != 0)
                    whiteSum++;

                if ((int)(motion_mask.at<uchar>(by+j,bx+i)) != 0)
                    blackSum++;
            }            
        }
        int wht = 127;
        string holder = "Unknown";

        if (whiteSum>(blackSum*1.10) && count > 400) {
            wht = 255;
            holder = "White Team";
        } else if (whiteSum<(blackSum*0.90) && count > 400) {
            wht = 0;
            holder = "Black Team";
        }

        //cout << whiteSum << " " << blackSum << endl;
        //rectangle(frame, whiteRegion, Scalar( 0, wht, 255-wht ), 1, 1 );
        //rectangle(frame, blackRegion, Scalar( 0, 255-wht, wht ), 1, 1 );

        cv::putText(frame, //target image
            "Frame: " + to_string((int) count)  + "/2240", //text
            cv::Point(10, 130), //top-left position
            cv::FONT_HERSHEY_DUPLEX,
            0.8,
            CV_RGB(255, 255, 255), //font color
            1);

       cv::putText(frame, //target image
            "Ball possession: " +  holder, //text
            cv::Point(10, 105), //top-left position
            cv::FONT_HERSHEY_DUPLEX,
            0.8,
            CV_RGB(255-wht, wht, 0), //font color
            1);

        outputVideo << frame;
        imshow("basket",frame);

        waitKey(1);
    }

    return 0;
}