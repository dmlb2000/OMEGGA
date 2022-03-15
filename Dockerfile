FROM kbase/sdkbase2:latest
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONVER=3.8.12
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev vim && \
    apt-get clean all
RUN curl -Lo - https://www.python.org/ftp/python/${PYTHONVER}/Python-${PYTHONVER}.tgz | tar -C /usr/src -xzf -
RUN cd /usr/src/Python-${PYTHONVER} && \
    ./configure --enable-optimizations && \
    make -j4 && \
    make altinstall
RUN /usr/local/bin/python3.8 -m pip install --upgrade pip setuptools wheel && \
    /usr/local/bin/python3.8 -m pip install jinja2 numpy requests sphinx uwsgi nose jsonrpc jsonrpcbase coverage jinja2 pandas
# -----------------------------------------
RUN mkdir -p /kb/module/data
RUN curl -Lo /kb/module/data/reactions.tsv https://raw.githubusercontent.com/ModelSEED/ModelSEEDDatabase/master/Biochemistry/reactions.tsv
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
