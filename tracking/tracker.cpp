#include <iostream>
#include <fstream>
#include <cstdlib>
#include <string>
#include <vector> 

#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/tracking.hpp>
#include <opencv2/core/utility.hpp>

using namespace std;
using namespace cv;

int main(int argc, char const *argv[]) {
	int debug = 0;

	Mat frame;
	VideoCapture cap;
	VideoWriter outputVideo;      

	int tracker_count = 3;
	Ptr<Tracker> trackers[] = {TrackerCSRT::create(),TrackerCSRT::create(),TrackerCSRT::create()};

	if (argc != 3){
		cout << "\nError found:" << "Incorrect arguments." << "\nTerminating.\n\nRun using this command:\n\n\t" << "./track <video> <debug>\n\n";
		return -1;
	}

	string x,y,width,height;
	string shift;
	ifstream boxes;
	boxes.open ("boxes.txt");
	boxes >> x >> y >> width >> height;
	boxes >> shift;

	namedWindow("tracker",WINDOW_AUTOSIZE);

	cap.open(argv[1]);
	debug = atoi(argv[2]);

	if (!cap.isOpened())
		return -2;

	Size S = Size((int) cap.get(CAP_PROP_FRAME_WIDTH),(int) cap.get(CAP_PROP_FRAME_HEIGHT));
    outputVideo.open("../output/tracker.mp4", static_cast<int>(cap.get(CAP_PROP_FOURCC)), cap.get(CAP_PROP_FPS), S, true);

	Rect2i roi[] = {Rect2i(stoi(x),stoi(y),stoi(width),stoi(height)),
					Rect2i(stoi(x)-stoi(shift),stoi(y),stoi(width),stoi(height)),
					Rect2i(stoi(x)+stoi(shift),stoi(y),stoi(width),stoi(height))};

	cap >> frame;
    outputVideo << frame;

	vector<Point2i> trackedpoints = vector<Point2i>();
	trackedpoints.push_back((roi[0].br() + roi[0].tl())*0.5);

	for (int i = 0; i < tracker_count; ++i)
		trackers[i]->init(frame,roi[i]);

	double threshold = 6.95;
	double count = 0.0;
	double distances[] = {0.0,0.0,0.0};
	double sum[] = {0.0,0.0,0.0};
	double var[] = {0.0,0.0,0.0};
	bool tracker_situation[] = {true,true,true};

	while(true){
		count += 1;
		cap >> frame;

        if (frame.empty())
            break;

		Point2i centers[] = {Point2i(0,0),Point2i(0,0),Point2i(0,0)};

		for (int i = 0; i < tracker_count; ++i){
			trackers[i]->update(frame,roi[i]);
			centers[i] = (roi[i].br() + roi[i].tl())*0.5;
		}

		if ((int)count % 4 == 0)
			trackedpoints.push_back(centers[0]);

		distances[0] = norm(Mat(centers[0]),Mat(centers[1]));
		distances[1] = norm(Mat(centers[0]),Mat(centers[2]));
		distances[2] = norm(Mat(centers[2]),Mat(centers[1]));

		for (int i = 0; i < tracker_count; ++i) {
			sum[i] += distances[i];
			var[i] = abs(distances[i]-sum[i]/count);
		}

		tracker_situation[0] = var[0] < threshold || var[1] < threshold;
		tracker_situation[1] = var[0] < threshold || var[2] < threshold;
		tracker_situation[2] = var[1] < threshold || var[2] < threshold;

		if (debug == 1){
			cout << (!tracker_situation[0]?"\033[91m":"\033[92m") << "Main Traker \033[0m" << endl;
			cout << (!tracker_situation[1]?"\033[91m":"\033[92m") << "Left Traker \033[0m" << endl;
			cout << (!tracker_situation[2]?"\033[91m":"\033[92m") << "Right Traker \033[0m" << endl <<endl;
		}

		Point2i roi_candidates_tl(0,0);
		Size2f roi_candidates_size(0,0);

		int conc = 0;
		for (int i = 0; i < tracker_count; ++i) {
			if (tracker_situation[i]){
				conc += 1;
				roi_candidates_tl += roi[i].tl();
				roi_candidates_size += Size2f(roi[0].size().width*0.98f,roi[0].size().height*0.98f);
			}
		} 

		if (conc == 0) {
			conc += 1;
			roi_candidates_tl += roi[0].tl();
			roi_candidates_size += Size2f(roi[0].size().width*0.98f,roi[0].size().height*0.98f);
		}

		roi_candidates_tl = roi_candidates_tl / conc;
		roi_candidates_size = Size2f(roi_candidates_size / (float) conc);

		Rect2i roi_candidate = Rect2i(roi_candidates_tl,roi_candidates_size);
		if (debug == 1)
			cout << roi_candidate << endl;

		for (int i = 0; i < tracker_count; ++i) {
			if(!tracker_situation[i]){
				//trackers[i]->~Tracker();
				trackers[i] = TrackerCSRT::create();
				
				Point2i displacement = Point2i(0,0);
				if (i == 1)
					displacement = Point2i(+stoi(shift),0);
				else if (i == 2)
					displacement = Point2i(-stoi(shift),0);

				trackers[i]->init(frame,roi_candidate+displacement);
				
				if (debug == 1)	
					cout << "RESET" <<endl;
			}
		}

		rectangle(frame, roi[0], Scalar( 255, 127, 127 ), 2, 1 );
		rectangle(frame, roi[1], Scalar( 127, 255, 127 ), 2, 1 );
		rectangle(frame, roi[2], Scalar( 127, 127, 255 ), 2, 1 );
		rectangle(frame, roi_candidate, Scalar( 0, 0, 0 ), 2, 1 );

		const Point* pts = (const Point*) Mat(trackedpoints).data;
		int npts = Mat(trackedpoints).rows;
		polylines(frame, &pts, &npts, 1, false, Scalar(255, 0, 0));

		cv::putText(frame, //target image
			"Frame: " + to_string((int) count)  + "/2240", //text
			cv::Point(10, 130), //top-left position
			cv::FONT_HERSHEY_DUPLEX,
			0.8,
			CV_RGB(255, 255, 255), //font color
			1);

    	outputVideo << frame;
		if (debug >= 1)
			imshow("tracker",frame);

		if(waitKey(1)>=0) 
			break;
	}

	return 0;
}