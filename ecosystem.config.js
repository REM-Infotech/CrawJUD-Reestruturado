module.exports = {
  apps: [
    {
      name: "crawjud_app",
      cmd: "celery_app",
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
  ],
};
