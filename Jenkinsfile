#!/usr/bin/env groovy

def user = 'artsalliancemedia'
def repo = 'thunderstorm-library'

node('aam-identity-prodcd') {
    properties([
        [
            $class: 'HudsonNotificationProperty',
            endpoints: [[
                event: 'all',
                format: 'JSON',
                loglines: 0,
                protocol: 'HTTP',
                timeout: 30000,
                url: 'https://webhooks.gitter.im/e/953b1e47e601cbf09ff8']]
        ],
        [
            $class: 'GithubProjectProperty',
            displayName: 'TS Lib',
            projectUrlStr: 'https://github.com/artsalliancemedia/thunderstorm-library/'
        ]
    ])


    stage('Checkout') {
        checkout scm
    }

    try {
        def registry = '886366864302.dkr.ecr.eu-west-1.amazonaws.com'
        // CODACY_PROJECT_TS_LIB_TOKEN is a global set in jenkins
        stage('Test') {
            withEnv([
              "REGISTRY=${registry}"
            ]) {
              parallel 'python34': {
                sh "docker-compose run -e CODACY_PROJECT_TOKEN=${env.CODACY_PROJECT_TS_LIB_TOKEN} -e PYTHON_VERSION=34 python34 make install test codacy"
                junit 'results-34.xml'
              }, 'python35': {
                sh "docker-compose run -e CODACY_PROJECT_TOKEN=${env.CODACY_PROJECT_TS_LIB_TOKEN} -e PYTHON_VERSION=35 python35 make install test codacy"
                junit 'results-35.xml'
              }, 'python36': {
                sh "docker-compose run -e CODACY_PROJECT_TOKEN=${env.CODACY_PROJECT_TS_LIB_TOKEN} -e PYTHON_VERSION=36 python36 make install test codacy"
                junit 'results-36.xml'
              }
            }
            sh 'docker-compose down'
        }

        // determine if release should be pushed: the most recent commit must contain string "[release]"
        def is_release = sh (script: 'git log --oneline --no-merges -1 | grep -q \'\\[release\\]\'', returnStatus: true)

        // master branch builds are pushed to Github
        if (env.BRANCH_NAME == 'master') {

            stage('Create Github Release') {

                if (is_release == 0) {
                  // extract application version
                  def version = sh (script: 'python setup.py --version', returnStdout: true).trim()
                  def prDetails = getLatestPRDetails()
                  // GITHUB_TOKEN is a global set in jenkins
                  withEnv([
                      "GITHUB_TOKEN=${env.GITHUB_TOKEN}",
                  ]) {
                    // create distribution
                    sh "make dist"
                    sh """
                        git remote set-url origin git@github.com:artsalliancemedia/thunderstorm-library.git
                        git tag -f v${version}
                        git push --tags
                        cat << EOF | github-release release -u ${user} -r ${repo} -t v${version} -d -
                        ${prDetails.body}
                        EOF
                        github-release upload -u '${user}' -r '${repo}' -t 'v${version}' -n 'thunderstorm-library-${version}.tar.gz' -f 'dist/thunderstorm-library-${version}.tar.gz'
                    """
                  }
              } else {
                  echo 'No [release] commit -- skipping'
              }
          }
      }
    } catch (err) {
        junit 'results-34.xml'
        junit 'results-35.xml'
        junit 'results-36.xml'
        error 'Thunderstorm library build failed ${err}'

    } finally {
        sh 'docker-compose down'
    }
}

def getLatestPRNumber() {
    return sh(
        script: "git log --merges -1 | grep -Eo '#[0-9]+' | sed 's/#//g'",
        returnStdout: true
    ).trim()
}

def getLatestPRDetails() {
    def prNumber = getLatestPRNumber()
    def url = "https://api.github.com/repos/artsalliancemedia/thunderstorm-library/pulls/${prNumber}"
    def prJSON = sh(
        script: "curl -H 'Authorization: token ${GITHUB_TOKEN}' ${url} | jq -c '{title: .title, body: .body}'",
        returnStdout: true
    )
    def prMap = [
        title: sh(script: "echo '${prJSON}' | jq -r '.title'", returnStdout: true),
        body: sh(script: "echo '${prJSON}' | jq -r '.body'", returnStdout: true),
    ]
    return prMap
}
