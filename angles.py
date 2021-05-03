import cv2
import math

INDICATOR_RADIUS = 10


class KeypointError(Exception):
    pass


def create_vector(point_1, point_2):
    return tuple([point_2[0] - point_1[0], point_2[1] - point_1[1]])


def collinear(point_1, point_2, point_3):
    """ Calculation the area of
        triangle. We have skipped
        multiplication with 0.5 to
        avoid floating point computations """
    distance_wrist_to_shoulder = math.sqrt((point_2[0] - point_3[0]) ** 2 + (point_2[1] - point_3[1]) ** 2)
    distance_elbow_to_shoulder = math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)
    a = point_1[0] * (point_2[1] - point_3[1]) + point_2[0] * (point_3[1] - point_1[1]) + point_3[0] * (
                point_1[1] - point_2[1])
    return abs(a / 2) < 7500 and distance_wrist_to_shoulder > 400 and distance_elbow_to_shoulder > 175


def output_angles(frame, analysis_dict, reference):
    y_pos = 20
    for key, value in analysis_dict.items():
        if key in reference.keys():
            text = "{}: Angle = {:.2f}, Diff = {:.2f}".format(key, value, value - reference[key])
            cv2.putText(frame, text, (0, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2,
                cv2.LINE_AA)
            cv2.putText(frame, text, (0, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1,
                        cv2.LINE_AA)
            y_pos += 20
    return frame


def calculate_heatmap_colour(reference, current):
    difference = abs(reference - current)
    green = max([0, 255 - (difference * 20)])
    red = 10 * difference
    color = (0, green, red)
    return color


def draw_keypoints(frame, keypoints, analysis_dict=None, reference=None):
    for key in keypoints.keys():
        position = tuple([int(keypoints[key][0]), int(keypoints[key][1])])
        if (key == "left_shoulder" or key == "right_shoulder") and reference is not None:
            cv2.circle(frame, position, INDICATOR_RADIUS, calculate_heatmap_colour(reference["shoulders"],
                                                                                   analysis_dict["shoulders"]),
                       cv2.FILLED)
        elif (key == "left_hip" or key == "right_hip") and reference is not None:
            cv2.circle(frame, position, INDICATOR_RADIUS, calculate_heatmap_colour(reference["hips"],
                                                                                   analysis_dict["hips"]), cv2.FILLED)
        elif reference is not None and key in analysis_dict.keys() and key in reference.keys():
            cv2.circle(frame, position, INDICATOR_RADIUS, calculate_heatmap_colour(reference[key], analysis_dict[key]),
                       cv2.FILLED)
    return frame


def calculate_tilt(lead, follow):
    y_change = lead[1] - follow[1]
    if y_change < 0:
        angle = calculate_angle(abs(y_change), abs(lead[0] - follow[0]))
    elif y_change > 0:
        angle = 0 - calculate_angle(abs(y_change), abs(lead[0] - follow[0]))
    else:
        angle = 0
    return angle


def calculate_limb(angle_point, point_1, point_2):
    vector_1 = create_vector(angle_point, point_1)
    vector_2 = create_vector(angle_point, point_2)
    angle = calculate_vector_angle(vector_1, vector_2)
    return angle


def calculate_lengths(angle_point, point_2):
    """
    Calculates the lengths of the side of the triangle needed to calculate the joint angles
    Returns longest side at index 0.
    """
    x_change = abs(angle_point[0] - point_2[0])
    y_change = abs(angle_point[1] - point_2[1])
    if angle_point[1] < point_2[1]:
        point_3 = [int(point_2[0]), int(point_2[1] - y_change)]
    else:
        point_3 = [int(angle_point[0]), int(angle_point[1] - y_change)]
    return tuple(point_3)


def calculate_analysis_dict(keypoints):
    analysis_dict = {
        "shoulders": calculate_tilt(keypoints["left_shoulder"], keypoints["right_shoulder"]),
        "hips": calculate_tilt(keypoints["left_hip"], keypoints["right_hip"]),
    }
    if "left_hip" in keypoints.keys() and "left_knee" in keypoints.keys() and "left_ankle" in keypoints.keys():
        analysis_dict["left_knee"] = calculate_limb(keypoints['left_knee'], keypoints["left_hip"],
                                                    keypoints["left_ankle"])
    if "right_hip" in keypoints.keys() and "right_knee" in keypoints.keys() and "right_ankle" in keypoints.keys():
        analysis_dict["right_knee"] = calculate_limb(keypoints['right_knee'], keypoints["right_hip"],
                                                     keypoints["right_ankle"])
    if "right_shoulder" in keypoints.keys() and "right_elbow" in keypoints.keys() and "right_wrist" in keypoints.keys():
        analysis_dict["right_elbow"] = calculate_limb(keypoints['right_elbow'], keypoints["right_shoulder"],
                                                      keypoints["right_wrist"])
    if "left_shoulder" in keypoints.keys() and "left_elbow" in keypoints.keys() and "left_wrist" in keypoints.keys():
        analysis_dict["left_elbow"] = calculate_limb(keypoints['left_elbow'], keypoints["left_shoulder"],
                                                     keypoints["left_wrist"])
    return analysis_dict


def dot_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]


def two_norm(v):
    return math.sqrt(dot_product(v, v))


def calculate_vector_angle(vector_1, vector_2):
    """
    Calculates the angle between two vectors.
    """
    dot = dot_product(vector_1, vector_2)
    cos_angle = float(dot / (two_norm(vector_1) * two_norm(vector_2)))
    # Buffer for floating point errors
    if 1.2 > cos_angle > 1:
        cos_angle = 1
    elif -1.2 < cos_angle < -1:
        cos_angle = -1
    elif -1.2 > cos_angle or 1.2 < cos_angle:
        raise KeypointError("Ratio for angle is outside of the domain.")
    if cos_angle > 0:
        multiplier = 1
    else:
        multiplier = -1
    angle_of_interest = (180 - math.degrees(math.acos(cos_angle))) * multiplier
    return angle_of_interest


def calculate_angle(opp, adjacent):
    """
    Calculates the angle of a right angle triangle
    """
    return math.degrees(math.atan((opp / adjacent)))


def angles_check(frame, predictions, reference, metadata):
    keypoints = get_keypoints(predictions, metadata)
    analysis_dict = calculate_analysis_dict(keypoints)
    vis_frame = draw_keypoints(frame, keypoints, analysis_dict, reference)
    vis_frame = output_angles(vis_frame, analysis_dict, reference)
    return vis_frame


def create_reference(frame, predictions, metadata):
    keypoints = get_keypoints(predictions, metadata)
    analysis_dict = calculate_analysis_dict(keypoints)
    vis_frame = draw_keypoints(frame, keypoints)
    return vis_frame, analysis_dict


def get_keypoints(predictions, metadata):
    if len(predictions) > 0:
        keypoint_names = metadata.get("keypoint_names")
        keypoints = predictions.get('pred_keypoints').squeeze()
        keypoint_dict = {
            "left_wrist": keypoints[keypoint_names.index('left_wrist')],
            "right_wrist": keypoints[keypoint_names.index('right_wrist')],
            "left_elbow": keypoints[keypoint_names.index('left_elbow')],
            "right_elbow": keypoints[keypoint_names.index('right_elbow')],
            "left_knee": keypoints[keypoint_names.index('left_knee')],
            "right_knee": keypoints[keypoint_names.index('right_knee')],
            "left_hip": keypoints[keypoint_names.index('left_hip')],
            "right_hip": keypoints[keypoint_names.index('right_hip')],
            "left_shoulder": keypoints[keypoint_names.index('left_shoulder')],
            "right_shoulder": keypoints[keypoint_names.index('right_shoulder')],
            "left_ankle": keypoints[keypoint_names.index('left_ankle')],
            "right_ankle": keypoints[keypoint_names.index('right_ankle')]
        }
        return keypoint_dict
    else:
        raise KeypointError("Predictions has length 0")
