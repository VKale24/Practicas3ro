 subtracted = cv2.subtract(imageRead2, imageRead1)
            b, g, r = cv2.split(subtracted)
 
            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                print("The images are completely Equal")
    
            else:
                print("the images are not equal")
            cv2.waitKey()
            #if result is True:
             #   print ("The images are the same")
            #else:
            #    print ("the images are different")
            cv2.destroyAllWindows()