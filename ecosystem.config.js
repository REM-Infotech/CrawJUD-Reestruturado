module.exports = {
  apps: [
    {
      name: "crawjud_app",
      cmd: "_crawjudapp.py",
      args: "--type worker",
      autorestart: true,
      watch: true,
      pid: "./.log/crawjud_app.pid",
      // max_memory_restart: '1G',
      // env: {
      //   ENV: 'development'
      // },
      // env_production : {
      //   ENV: 'production'
      // }
    },
    {
      name: "crawjud_api",
      cmd: "_apicrawjud.py",
      autorestart: true,
      watch: true,
      pid: "./.log/crawjud_api.pid",
      // max_memory_restart: '1G',
      // env: {
      //   ENV: 'development'
      // },
      // env_production : {
      //   ENV: 'production'
      // }
    },
  ],
};
