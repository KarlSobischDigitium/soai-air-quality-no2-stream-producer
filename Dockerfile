FROM continuumio/miniconda3

ENV PYTHONUNBUFFERED=1


RUN conda create -n env python=3.8
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH
RUN echo "**** copy source ****"
COPY ./requirements.txt /opt/
COPY ./main.py /opt/
COPY ./lib /opt/lib
COPY ./savedModels /opt/savedModels
COPY ./air-quality-backend /opt/air-quality-backend

RUN echo "**** install requirements.txt ****"
RUN pip install -r /opt/requirements.txt
ENTRYPOINT ["python" , "/opt/main.py"]