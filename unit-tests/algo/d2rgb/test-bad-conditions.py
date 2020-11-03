import pyrealsense2 as rs, test, ac

# We set the environment variables to suit this test
test.set_env_vars({"RS2_AC_DISABLE_CONDITIONS":"0",
                   "LOG_TO_STDOUT":"1"
                   })

# rs.log_to_file( rs.log_severity.debug, "rs.log" )

dev = test.get_first_device_or_exit()
depth_sensor = dev.first_depth_sensor()
color_sensor = dev.first_color_sensor()

d2r = rs.device_calibration(dev)
d2r.register_calibration_change_callback( ac.status_list_callback )

cp = next(p for p in color_sensor.profiles if p.fps() == 30
                and p.stream_type() == rs.stream.color
                and p.format() == rs.format.yuyv
                and p.as_video_stream_profile().width() == 1280
                and p.as_video_stream_profile().height() == 720)

dp = next(p for p in
                depth_sensor.profiles if p.fps() == 30
                and p.stream_type() == rs.stream.depth
                and p.format() == rs.format.z16
                and p.as_video_stream_profile().width() == 1024
                and p.as_video_stream_profile().height() == 768)

depth_sensor.open( dp )
depth_sensor.start( lambda f: None )
color_sensor.open( cp )
color_sensor.start( lambda f: None )

#############################################################################################
test.start("Failing check_conditions function")
depth_sensor.set_option(rs.option.ambient_light, 2)
depth_sensor.set_option(rs.option.receiver_gain, 15)
try:
    d2r.trigger_device_calibration( rs.calibration_type.manual_depth_to_rgb )
    ac.wait_for_calibration()
except Exception as e:
    test.check_exception(e, RuntimeError)
else:
    test.check_no_reach()
test.check_equal_lists(ac.status_list, [rs.calibration_status.bad_conditions])
test.finish()
#############################################################################################
test.print_results_and_exit()