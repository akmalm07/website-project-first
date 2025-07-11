from flask import request, jsonify, g, Blueprint
import utils
import datetime


def generate_signed_url(bucket_name, object_name, duration_seconds=3600):
    """Generates a v4 signed URL for accessing a GCS object."""
    bucket = utils.VIDEO_STORAGE_CLIENT.bucket(bucket_name)
    blob = bucket.blob(object_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(seconds=duration_seconds),
        method="GET",
    )
    return url

def is_admin(data):
    return (data.get('username') == utils.AUTHORIZED_USER and
            data.get('passcode') == utils.AUTHORIZED_PASSCODE and
            data.get('secret') == utils.AUTHORIZED_SECRET)


video_bp = Blueprint("video", __name__, url_prefix=f"/api/videos")

@video_bp.route('/<user_id>/get_all_vids', methods=['GET'])
@utils.auth_required_subscribed
def get_videos(user_id):
    try:
        if g.user.get("userId") != user_id:
            return jsonify({"error": "Unauthorized access to this user"}), 403

        user_data = g.user.get("data")
        if not user_data:
            return jsonify({"error": "User does not exist"}), 400

        videos_ref = utils.database.collection(utils.VIDEOS_COLLECTION)
        videos = []
        for doc in videos_ref.stream():
            video_data = doc.to_dict()
            video_data['id'] = doc.id
            if 'url' in video_data:
                video_data['signedUrl'] = generate_signed_url(utils.VIDEO_BUCKET_NAME, video_data['url'])
            if 'poster' in video_data:
                video_data['signedPosterUrl'] = generate_signed_url(utils.VIDEO_BUCKET_NAME, video_data['poster'])
            videos.append(video_data)

        return jsonify({'videos': videos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@video_bp.route('/<user_id>/post_vid', methods=['POST'])
@utils.auth_required_subscribed
def add_video(user_id):
    try:
        data = request.get_json()
        if not all(key in data for key in ['title', 'gcsUrl', 'gcsPosterUrl']):
            return jsonify({'error': 'Missing required fields: title, gcsUrl, gcsPosterUrl'}), 400

        if not is_admin(data):
            return jsonify({"error": "Only the authorized admin can add videos"}), 403

        new_video = {
            'title': data['title'],
            'url': data['gcsUrl'],       # Store the GCS path/filename
            'poster': data['gcsPosterUrl'], # Store the GCS path/filename
            'description': data.get('description', ''),
            'uploadDate': datetime.datetime.now(datetime.UTC).isoformat(),
            'isFeatured': False
        }
        doc_ref = utils.database.collection(utils.VIDEOS_COLLECTION).add(new_video)
        return jsonify({'message': 'Video added successfully', 'id': doc_ref[1].id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@video_bp.route('/<user_id>/post_featured_vid', methods=['POST'])
@utils.auth_required_subscribed
def add_featured_video(user_id):
    try:
        if user_id != "admin-no-licence":
            return jsonify({"error": "Only the authorized user can add videos"}), 403

        data = request.get_json()
        if not all(key in data for key in ['title', 'gcsUrl', 'gcsPosterUrl']):
            return jsonify({'error': 'Missing required fields: title, gcsUrl, gcsPosterUrl'}), 400

        if data.get('username') != utils.AUTHORIZED_USER or data.get('passcode') != utils.AUTHORIZED_PASSCODE or data.get('secret') != utils.AUTHORIZED_SECRET:
            return jsonify({"error": "Only the authorized user can add videos"}), 403

        new_video = {
            'title': data['title'],
            'url': data['gcsUrl'],       # Store the GCS path/filename
            'poster': data['gcsPosterUrl'], # Store the GCS path/filename
            'description': data.get('description', ''),
            'uploadDate': datetime.datetime.now(datetime.UTC).isoformat(),
            'isFeatured': True
        }

        #Erase the previous featured videos
        videos_ref = utils.database.collection(utils.VIDEOS_COLLECTION)
        existing_featured = videos_ref.where('isFeatured', '==', True).stream()
        for doc in existing_featured:
            doc.reference.update({'isFeatured': False})

        doc_ref = utils.database.collection(utils.VIDEOS_COLLECTION).add(new_video)
        return jsonify({'message': 'Video added successfully', 'id': doc_ref[1].id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@video_bp.route('/<user_id>/get_featured_vid', methods=['GET'])
@utils.auth_required_subscribed
def get_featured_video(user_id):
    try:
        if g.user.get("userId") != user_id:
            return jsonify({"error": "Unauthorized access to this user"}), 403

        user_data = g.user.get("data")
        if not user_data:
            return jsonify({"error": "User does not exist"}), 400

        videos_ref = utils.database.collection(utils.VIDEOS_COLLECTION)
        featured_video_doc = videos_ref.where('isFeatured', '==', True).limit(1).get()
        featured_video = None
        if featured_video_doc:
            for doc in featured_video_doc:
                featured_video = doc.to_dict()
                featured_video['id'] = doc.id
                if 'url' in featured_video:
                    featured_video['signedUrl'] = generate_signed_url(utils.VIDEO_BUCKET_NAME, featured_video['url'])
                if 'poster' in featured_video:
                    featured_video['signedPosterUrl'] = generate_signed_url(utils.VIDEO_BUCKET_NAME, featured_video['poster'])
                break

        if featured_video:
            return jsonify({'featuredVideo': featured_video}), 200
        else:
            return jsonify({'message': 'No featured video found.'}), 200  # Or a 404 if that's more appropriate
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@video_bp.route('/<user_id>/get-vid/<video_id>', methods=['GET'])
@utils.auth_required_subscribed
def get_individual_video(user_id, video_id):
    try:
        if g.user.get("userId") != user_id:
            return jsonify({"error": "Unauthorized access to this user"}), 403

        user_data = g.user.get("data")
        if not user_data:
            return jsonify({"error": "User does not exist"}), 400

        doc_ref = utils.database.collection(utils.VIDEOS_COLLECTION).document(video_id)
        video_data = doc_ref.get().to_dict()
        if video_data and 'url' in video_data:
            signed_url = generate_signed_url(utils.VIDEO_BUCKET_NAME, video_data['url'])
            return jsonify({'signedUrl': signed_url}), 200
        else:
            return jsonify({'error': 'Video not found or URL missing'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

