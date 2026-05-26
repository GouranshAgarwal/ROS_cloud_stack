from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([

        # Gazebo
        ExecuteProcess(
            cmd=[
                'bash', '-c',
                'export IGN_RENDER_ENGINE=ogre2 && '
                'export LIBGL_ALWAYS_SOFTWARE=1 && '
                'ign gazebo -s -r /ros_ws/src/sim_pkg/sim_pkg/worlds/camera_world.sdf'
            ],
            output='screen'
        ),

        # Bridge
        ExecuteProcess(
            cmd=[
                'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                '/camera@sensor_msgs/msg/Image@gz.msgs.Image'
            ],
            output='screen'
        ),

        ExecuteProcess(
            cmd=[
                'ros2', 'run', 'sim_pkg', 'image_publisher'
            ],
            output='screen'
        ),

        # 🔥 YOUR NODE (add this)
        Node(
            package='sim_pkg',
            executable='camera_node',
            output='screen'
        ),

        Node(
            package='sim_pkg',
            executable='decision_node',
            output='screen'
        )

    ])