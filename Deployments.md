Deployments
===========

These are the steps to deploy a new version of the server and frontend to production.

1. SSH into the server.
   `ssh <user>@<host>`
2. Navigate to the Ravel project directory
   `cd ravel/ravel/`
3. Activate the Python Environment
   `source api/venv/bin/activate`
4. Pull most recent git version
   `git pull origin master`
5. Restart the server
   From the root of the project directory, run
   `pm2 restart run`
   You should see an output of the running processes. Check to make sure it's not stuck in a boot loop.
6. Navigate into the `ui` folder and rebuild the front end
   `cd ui/ && npm run build`
7. Verify that everything is working correctly in prod by testing uploads
   and downloads on your account.
