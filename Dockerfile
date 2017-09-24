FROM python:3.5-alpine

# Copy in requirements file
ADD requirements.txt /requirements.txt

# Or, if using a directory for requirements, copy everything (comment out the above
# and uncomment this if so):
#: Add requirements /requirements

# Install build deps, then run `pip install`, then remove unneeded build deps all in
# a single step. Correct the path to production requirements file, if needed.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            libffi-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
    && pyvenv /venv \
    && /venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir -r /requirements.txt" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# Copy application code to the container (make sure to create a .dockerignore 
# file if any large files or directories should be excluded)
RUN mkdir -p /app/code/
WORKDIR /app/code/
ADD . /app/code/

# install other dependencies
RUN /venv/bin/pip install /app/code/.libs/elixr.base*.whl \
 && /venv/bin/pip install /app/code/.libs/elixr.sax*.whl \
 && /venv/bin/pip install -e .

# waitress will listen on this port
EXPOSE 9876

# serve app
CMD ["/venv/bin/pserve", "production.ini"]
