# README #

This README would normally document whatever steps are necessary to get your application up and running.

### The turtlebot multiagent path-finding demo ###

* Quick summary
  - This server holds the planned paths for the turtlebot agents.
  - Agents query the sever with `GET /?agent_id=<num>` for the next position to move to receiving the format in `get_success.json`
  - While moving, agents `POST /` with the format in `post_success.json`
  - In the online planning mode:
    - A planning server can query the agent states to plan from with `GET /get_locations` api, an example return is `get_locations.json`
    - They can also add steps to agent plans with `POST /extend_path` with the format at `post_extend_path.json`

### How do I set up a running demo? ###

* Summary of set up
  - Start the CentralController with `python main.py`
  - For an OnlineExecutionPolciy Use `path_uploader.py` with a `path.txt` to provide the plan to the server
  - Now start the agents, turtlebot agents were implemented at [spl_turtlebot4](https://github.com/Jayden-F/spl_turtlebot4)
* Server Configuration
  - The CentralController listens over TCP at a configured port on the local machine,
  the outwards facing IP must be bound (i.e 192.) for other hosts on the LAN or public networks to
  connect to the CentralController.
    - A localhost or (127.0.0.1 ipv4 or ::1 ipv6) address will only be visible to other programs on the same machine.
  - A "no route to host" error for a client implies that no host responded to the requested ip and port configuration.
  This can be due to invalid configuration or the firewall on the server blocking the requested port for external IPs
* Client configuration for turtlebots under spl_turtlebot4
  - This is documentation for the cpp turtlebot launch
  1. Basic ROS2 setup (INCOMPLETE DOCS)
    - Install ROS2 humble at [ROS2 docs](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html)
    - Enter the `ros2_ws` and run `colcon build --symlink-install` *Prefer to symlink over copying non-compiled files*
    - Begin with `bash install/setup.bash` from ros2_ws for autocompletions
    - Launch the navigation system with `ros2 launch spl_bringup turtlebot4`
      - A lidar map can be configured at (INCOMPLETE)
      - A lidar map can also be generated 
    - Launch the commander server to query the `ros2 run commander_server turtlebot_commander`
      - The ip and port of the server can be configured with the `--ip 192.168.0.144` and `--port 8080`
      - The agent_id of the agent is assigned with `--id 0`  
  - Generating a lidar scan map (INCOMPLETE)
    - Run the navigation server in SLAM mode 
      - This comes from the nav2 library used
    - Move the robot with `ros2 run teleop_twist_keyboard teleop_twist_keyboard`
      - This is installed alongside ros2 humble
